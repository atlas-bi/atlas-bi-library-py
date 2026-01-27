import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connections, transaction

from atlas_index.models import (
    AtlasUser,
    Collection,
    CollectionReport,
    Groups,
    Initiative,
    MaintenanceLog,
    ReportObjectDocFragilityTags,
    ReportObjectDocMaintenanceLogs,
    ReportObjectDocTerms,
    ReportObjectHierarchy,
    ReportObjectQuery,
    ReportObjectType,
    RolePermissionLinks,
    RolePermissions,
    Tag,
    UserGroupMemberships,
    UserRoleLinks,
    UserRoles,
)


class Command(BaseCommand):
    help = "Seed Turbo-owned SQL Server (dg_db) with starter Atlas-style data."

    def handle(self, *args, **options):
        using = "dg_db"

        seed_sql_path = os.environ.get("ATLAS_DEMO_SEED_SQL_PATH", "").strip()
        if not seed_sql_path:
            guess = (
                Path(__file__).resolve().parents[5]
                / "Library"
                / "web"
                / "atlas-demo-seed_script.sql"
            )
            seed_sql_path = str(guess)

        seed_sql_file = Path(seed_sql_path)
        if not seed_sql_file.exists():
            raise RuntimeError(
                f"ATLAS_DEMO_SEED_SQL_PATH not found: {seed_sql_path}. "
                "Set ATLAS_DEMO_SEED_SQL_PATH to the legacy atlas-demo-seed_script.sql file."
            )

        seed_sql_text = seed_sql_file.read_text(encoding="utf-8", errors="ignore")

        def _find_between(text: str, start: str, end: str) -> str:
            sidx = text.lower().find(start.lower())
            if sidx < 0:
                raise RuntimeError(f"Seed section start not found: {start}")
            eidx = text.lower().find(end.lower(), sidx)
            if eidx < 0:
                raise RuntimeError(f"Seed section end not found: {end}")
            return text[sidx:eidx]

        def _parse_sql_value(tok: str):
            t = tok.strip()
            if not t:
                return ""
            if t.upper() == "NULL":
                return None
            if t.startswith("N'") and t.endswith("'"):
                return t[2:-1].replace("''", "'")
            if t.startswith("'") and t.endswith("'"):
                return t[1:-1].replace("''", "'")
            try:
                if "." in t:
                    return float(t)
                return int(t)
            except ValueError:
                return t

        def _parse_values_tuples(values_sql: str) -> list[list[object]]:
            tuples: list[list[object]] = []
            i = 0
            n = len(values_sql)
            while i < n:
                while i < n and values_sql[i].isspace():
                    i += 1
                if i >= n:
                    break
                if values_sql[i] != "(":
                    i += 1
                    continue
                i += 1
                fields: list[str] = []
                buf: list[str] = []
                in_str = False
                while i < n:
                    ch = values_sql[i]
                    if in_str:
                        buf.append(ch)
                        if ch == "'":
                            if i + 1 < n and values_sql[i + 1] == "'":
                                buf.append("'")
                                i += 2
                                continue
                            in_str = False
                        i += 1
                        continue

                    if ch == "'":
                        in_str = True
                        buf.append(ch)
                        i += 1
                        continue

                    if ch == ",":
                        fields.append("".join(buf).strip())
                        buf = []
                        i += 1
                        continue

                    if ch == ")":
                        fields.append("".join(buf).strip())
                        i += 1
                        break

                    buf.append(ch)
                    i += 1

                tuples.append([_parse_sql_value(f) for f in fields])
            return tuples

        def _extract_insert_values_block(
            table: str,
        ) -> tuple[list[str], list[list[object]]]:
            lower = seed_sql_text.lower()
            marker = f"insert into {table}".lower()
            sidx = lower.find(marker)
            if sidx < 0:
                raise RuntimeError(f"Insert not found for {table}")
            go_idx = lower.find("\ngo", sidx)
            if go_idx < 0:
                go_idx = len(seed_sql_text)
            block = seed_sql_text[sidx:go_idx]

            open_paren = block.find("(")
            close_paren = block.find(")", open_paren + 1)
            if open_paren < 0 or close_paren < 0:
                raise RuntimeError(f"Could not parse column list for {table}")

            columns_sql = block[open_paren + 1 : close_paren]
            columns = [c.strip().strip("[]") for c in columns_sql.split(",")]

            values_idx = block.lower().find(" values", close_paren)
            if values_idx < 0:
                raise RuntimeError(f"Could not locate VALUES for {table}")
            values_sql = block[values_idx + len(" values") :]
            rows = _parse_values_tuples(values_sql)
            return columns, rows

        def _extract_values_list(start: str, end: str) -> list[list[object]]:
            chunk = _find_between(seed_sql_text, start, end)
            v_idx = chunk.lower().find("values")
            if v_idx < 0:
                raise RuntimeError(f"VALUES not found in section: {start}")
            return _parse_values_tuples(chunk[v_idx + len("values") :])

        def _extract_values_list_in_section(
            section_start: str,
            section_end: str,
            values_marker: str = "values",
        ) -> list[list[object]]:
            chunk = _find_between(seed_sql_text, section_start, section_end)
            v_idx = chunk.lower().find(values_marker.lower())
            if v_idx < 0:
                raise RuntimeError(f"VALUES not found in section: {section_start}")
            return _parse_values_tuples(chunk[v_idx + len(values_marker) :])

        seed_users: list[tuple[int, str, str, str, str, str, str, str]] = [
            (
                1,
                "Hertha-Barham",
                "Hertha Barham",
                "Hertha",
                "Barham",
                "Accident and Emergency",
                "Boss",
                "hBarham@my_hosptital.rocks",
            ),
            (
                2,
                "Amada-Tisdale",
                "Amada Tisdale",
                "Amada",
                "Tisdale",
                "Accident and Emergency",
                "Worker",
                "aTisdale@my_hosptital.rocks",
            ),
            (
                3,
                "Bryce-Bayne",
                "Bryce Bayne",
                "Bryce",
                "Bayne",
                "Accident and Emergency",
                "Manager",
                "bBayne@my_hosptital.rocks",
            ),
            (
                4,
                "Hae-Weiner",
                "Hae Weiner",
                "Hae",
                "Weiner",
                "Accident and Emergency",
                "Mr Cool",
                "hWeiner@my_hosptital.rocks",
            ),
            (
                5,
                "Shonda-Purcell",
                "Shonda Purcell",
                "Shonda",
                "Purcell",
                "Accident and Emergency",
                "Do it right",
                "sPurcell@my_hosptital.rocks",
            ),
            (
                6,
                "Earle-Archuleta",
                "Earle Archuleta",
                "Earle",
                "Archuleta",
                "Accident and Emergency",
                "First at Work",
                "eArchuleta@my_hosptital.rocks",
            ),
            (
                7,
                "Garth-Cornwell",
                "Garth Cornwell",
                "Garth",
                "Cornwell",
                "Accident and Emergency",
                "Worker",
                "gCornwell@my_hosptital.rocks",
            ),
            (
                8,
                "Mardell-Crews",
                "Mardell Crews",
                "Mardell",
                "Crews",
                "Accident and Emergency",
                "Worker",
                "mCrews@my_hosptital.rocks",
            ),
            (
                9,
                "Jade-Wiggins",
                "Jade Wiggins",
                "Jade",
                "Wiggins",
                "Accident and Emergency",
                "Worker",
                "jWiggins@my_hosptital.rocks",
            ),
            (
                10,
                "Marylee-Rauch",
                "Marylee Rauch",
                "Marylee",
                "Rauch",
                "Accident and Emergency",
                "Worker",
                "mRauch@my_hosptital.rocks",
            ),
            (
                11,
                "Magda-Shook",
                "Magda Shook",
                "Magda",
                "Shook",
                "Accident and Emergency",
                "Worker",
                "mShook@my_hosptital.rocks",
            ),
            (
                12,
                "Nannie-Redmond",
                "Nannie Redmond",
                "Nannie",
                "Redmond",
                "Accident and Emergency",
                "Boss",
                "nRedmond@my_hosptital.rocks",
            ),
            (
                13,
                "Candance-Singer",
                "Candance Singer",
                "Candance",
                "Singer",
                "Accident and Emergency",
                "Worker",
                "cSinger@my_hosptital.rocks",
            ),
            (
                14,
                "Renata-Bigelow",
                "Renata Bigelow",
                "Renata",
                "Bigelow",
                "Accident and Emergency",
                "Manager",
                "rBigelow@my_hosptital.rocks",
            ),
            (
                15,
                "Eve-Wilkinson",
                "Eve Wilkinson",
                "Eve",
                "Wilkinson",
                "Accident and Emergency",
                "Mr Cool",
                "eWilkinson@my_hosptital.rocks",
            ),
            (
                16,
                "Tiesha-Chavis",
                "Tiesha Chavis",
                "Tiesha",
                "Chavis",
                "Admissions",
                "Do it right",
                "tChavis@my_hosptital.rocks",
            ),
            (
                17,
                "Bernardine-Scherer",
                "Bernardine Scherer",
                "Bernardine",
                "Scherer",
                "Admissions",
                "First at Work",
                "bScherer@my_hosptital.rocks",
            ),
            (
                18,
                "Stefania-Wakefield",
                "Stefania Wakefield",
                "Stefania",
                "Wakefield",
                "Admissions",
                "Worker",
                "sWakefield@my_hosptital.rocks",
            ),
            (
                19,
                "Roselia-Hoskins",
                "Roselia Hoskins",
                "Roselia",
                "Hoskins",
                "Admissions",
                "Worker",
                "rHoskins@my_hosptital.rocks",
            ),
            (
                20,
                "Hyun-Rockwell",
                "Hyun Rockwell",
                "Hyun",
                "Rockwell",
                "Admissions",
                "Worker",
                "hRockwell@my_hosptital.rocks",
            ),
            (
                21,
                "Marcelina-Brinson",
                "Marcelina Brinson",
                "Marcelina",
                "Brinson",
                "Admissions",
                "Worker",
                "mBrinson@my_hosptital.rocks",
            ),
            (
                22,
                "Grazyna-Peter",
                "Grazyna Peter",
                "Grazyna",
                "Peter",
                "Admissions",
                "Worker",
                "gPeter@my_hosptital.rocks",
            ),
            (
                23,
                "Yuko-Manley",
                "Yuko Manley",
                "Yuko",
                "Manley",
                "Admissions",
                "Boss",
                "yManley@my_hosptital.rocks",
            ),
            (
                24,
                "Lizzie-Olivas",
                "Lizzie Olivas",
                "Lizzie",
                "Olivas",
                "Admissions",
                "Worker",
                "lOlivas@my_hosptital.rocks",
            ),
            (
                25,
                "Barbar-Durand",
                "Barbar Durand",
                "Barbar",
                "Durand",
                "Admissions",
                "Manager",
                "bDurand@my_hosptital.rocks",
            ),
            (
                26,
                "Jung-Romano",
                "Jung Romano",
                "Jung",
                "Romano",
                "Admissions",
                "Mr Cool",
                "jRomano@my_hosptital.rocks",
            ),
            (
                27,
                "Theola-Blanchette",
                "Theola Blanchette",
                "Theola",
                "Blanchette",
                "Cardiology",
                "Do it right",
                "tBlanchette@my_hosptital.rocks",
            ),
            (
                28,
                "Patrick-Watters",
                "Patrick Watters",
                "Patrick",
                "Watters",
                "Cardiology",
                "First at Work",
                "pWatters@my_hosptital.rocks",
            ),
            (
                29,
                "Camila-Theriault",
                "Camila Theriault",
                "Camila",
                "Theriault",
                "Cardiology",
                "Worker",
                "cTheriault@my_hosptital.rocks",
            ),
            (
                30,
                "Golda-Henke",
                "Golda Henke",
                "Golda",
                "Henke",
                "Cardiology",
                "Worker",
                "gHenke@my_hosptital.rocks",
            ),
            (
                31,
                "Alysia-Casteel",
                "Alysia Casteel",
                "Alysia",
                "Casteel",
                "Cardiology",
                "Worker",
                "aCasteel@my_hosptital.rocks",
            ),
            (
                32,
                "Livia-Crayton",
                "Livia Crayton",
                "Livia",
                "Crayton",
                "Oncology",
                "Worker",
                "lCrayton@my_hosptital.rocks",
            ),
            (
                33,
                "Matilde-Alonzo",
                "Matilde Alonzo",
                "Matilde",
                "Alonzo",
                "Oncology",
                "Worker",
                "mAlonzo@my_hosptital.rocks",
            ),
            (
                34,
                "Cleora-Parnell",
                "Cleora Parnell",
                "Cleora",
                "Parnell",
                "Oncology",
                "Boss",
                "cParnell@my_hosptital.rocks",
            ),
            (
                35,
                "Willette-Marr",
                "Willette Marr",
                "Willette",
                "Marr",
                "Oncology",
                "Worker",
                "wMarr@my_hosptital.rocks",
            ),
            (
                36,
                "Eddie-Pereira",
                "Eddie Pereira",
                "Eddie",
                "Pereira",
                "Oncology",
                "Manager",
                "ePereira@my_hosptital.rocks",
            ),
            (
                37,
                "Evelin-Petersen",
                "Evelin Petersen",
                "Evelin",
                "Petersen",
                "Oncology",
                "Mr Cool",
                "ePetersen@my_hosptital.rocks",
            ),
            (
                38,
                "Michaela-Mckeown",
                "Michaela Mckeown",
                "Michaela",
                "Mckeown",
                "Oncology",
                "Do it right",
                "mMckeown@my_hosptital.rocks",
            ),
            (
                39,
                "Reyna-Blum",
                "Reyna Blum",
                "Reyna",
                "Blum",
                "Pharmacy",
                "First at Work",
                "rBlum@my_hosptital.rocks",
            ),
            (
                40,
                "Gail-Sapp",
                "Gail Sapp",
                "Gail",
                "Sapp",
                "Pharmacy",
                "Worker",
                "gSapp@my_hosptital.rocks",
            ),
            (
                41,
                "Giselle-Sams",
                "Giselle Sams",
                "Giselle",
                "Sams",
                "Pharmacy",
                "Worker",
                "gSams@my_hosptital.rocks",
            ),
            (
                42,
                "Rhona-Whiting",
                "Rhona Whiting",
                "Rhona",
                "Whiting",
                "Pharmacy",
                "Worker",
                "rWhiting@my_hosptital.rocks",
            ),
            (
                43,
                "Merrill-Hirsch",
                "Merrill Hirsch",
                "Merrill",
                "Hirsch",
                "Pharmacy",
                "Worker",
                "mHirsch@my_hosptital.rocks",
            ),
            (
                44,
                "Vina-Winchester",
                "Vina Winchester",
                "Vina",
                "Winchester",
                "Pharmacy",
                "Worker",
                "vWinchester@my_hosptital.rocks",
            ),
            (
                45,
                "Ronnie-Nickerson",
                "Ronnie Nickerson",
                "Ronnie",
                "Nickerson",
                "Pharmacy",
                "Boss",
                "rNickerson@my_hosptital.rocks",
            ),
            (
                46,
                "Corrine-Landry",
                "Corrine Landry",
                "Corrine",
                "Landry",
                "Pharmacy",
                "Worker",
                "cLandry@my_hosptital.rocks",
            ),
            (
                47,
                "Andrew-Janssen",
                "Andrew Janssen",
                "Andrew",
                "Janssen",
                "Radiotherapy",
                "Manager",
                "aJanssen@my_hosptital.rocks",
            ),
            (
                48,
                "Fatimah-Sheehan",
                "Fatimah Sheehan",
                "Fatimah",
                "Sheehan",
                "Radiotherapy",
                "Mr Cool",
                "fSheehan@my_hosptital.rocks",
            ),
            (
                49,
                "Andrea-Rainey",
                "Andrea Rainey",
                "Andrea",
                "Rainey",
                "Radiotherapy",
                "Do it right",
                "aRainey@my_hosptital.rocks",
            ),
            (
                50,
                "John-Knutson",
                "John Knutson",
                "John",
                "Knutson",
                "Radiotherapy",
                "First at Work",
                "jKnutson@my_hosptital.rocks",
            ),
            (
                51,
                "Andre-Meredith",
                "Andre Meredith",
                "Andre",
                "Meredith",
                "Radiotherapy",
                "Worker",
                "aMeredith@my_hosptital.rocks",
            ),
            (
                52,
                "Dalene-Binkley",
                "Dalene Binkley",
                "Dalene",
                "Binkley",
                "Radiotherapy",
                "Worker",
                "dBinkley@my_hosptital.rocks",
            ),
            (
                53,
                "Shaquana-Neeley",
                "Shaquana Neeley",
                "Shaquana",
                "Neeley",
                "Radiotherapy",
                "Worker",
                "sNeeley@my_hosptital.rocks",
            ),
            (
                54,
                "Willy-Jarvis",
                "Willy Jarvis",
                "Willy",
                "Jarvis",
                "Radiotherapy",
                "Worker",
                "wJarvis@my_hosptital.rocks",
            ),
            (
                55,
                "Dirk-Palma",
                "Dirk Palma",
                "Dirk",
                "Palma",
                "Radiotherapy",
                "Worker",
                "dPalma@my_hosptital.rocks",
            ),
            (
                56,
                "Raphael-Albers",
                "Raphael Albers",
                "Raphael",
                "Albers",
                "Radiotherapy",
                "Boss",
                "rAlbers@my_hosptital.rocks",
            ),
            (
                57,
                "Kenya-Durham",
                "Kenya Durham",
                "Kenya",
                "Durham",
                "Radiotherapy",
                "Worker",
                "kDurham@my_hosptital.rocks",
            ),
            (
                58,
                "Nikole-Janes",
                "Nikole Janes",
                "Nikole",
                "Janes",
                "Radiotherapy",
                "Manager",
                "nJanes@my_hosptital.rocks",
            ),
            (
                59,
                "Nigel-Grove",
                "Nigel Grove",
                "Nigel",
                "Grove",
                "Urology",
                "Mr Cool",
                "nGrove@my_hosptital.rocks",
            ),
            (
                60,
                "Wynona-Lancaster",
                "Wynona Lancaster",
                "Wynona",
                "Lancaster",
                "Urology",
                "Do it right",
                "wLancaster@my_hosptital.rocks",
            ),
            (
                61,
                "Delorse-Pence",
                "Delorse Pence",
                "Delorse",
                "Pence",
                "Urology",
                "First at Work",
                "dPence@my_hosptital.rocks",
            ),
            (
                62,
                "Claudie-Irwin",
                "Claudie Irwin",
                "Claudie",
                "Irwin",
                "Urology",
                "Worker",
                "cIrwin@my_hosptital.rocks",
            ),
            (
                63,
                "Roxane-Moreau",
                "Roxane Moreau",
                "Roxane",
                "Moreau",
                "Urology",
                "Worker",
                "rMoreau@my_hosptital.rocks",
            ),
            (
                64,
                "Jae-Clements",
                "Jae Clements",
                "Jae",
                "Clements",
                "Urology",
                "Worker",
                "jClements@my_hosptital.rocks",
            ),
            (
                65,
                "Milagro-Montalvo",
                "Milagro Montalvo",
                "Milagro",
                "Montalvo",
                "Urology",
                "Worker",
                "mMontalvo@my_hosptital.rocks",
            ),
            (
                66,
                "Lang-Dowling",
                "Lang Dowling",
                "Lang",
                "Dowling",
                "Urology",
                "Worker",
                "lDowling@my_hosptital.rocks",
            ),
            (
                67,
                "Myles-Fulton",
                "Myles Fulton",
                "Myles",
                "Fulton",
                "Analytics",
                "Boss",
                "mFulton@my_hosptital.rocks",
            ),
            (
                68,
                "Otelia-Bernstein",
                "Otelia Bernstein",
                "Otelia",
                "Bernstein",
                "Analytics",
                "Worker",
                "oBernstein@my_hosptital.rocks",
            ),
            (
                69,
                "Crystle-Homer",
                "Crystle Homer",
                "Crystle",
                "Homer",
                "Analytics",
                "Manager",
                "cHomer@my_hosptital.rocks",
            ),
            (
                70,
                "Lawana-Herron",
                "Lawana Herron",
                "Lawana",
                "Herron",
                "Analytics",
                "Mr Cool",
                "lHerron@my_hosptital.rocks",
            ),
            (
                71,
                "Ollie-Pinto",
                "Ollie Pinto",
                "Ollie",
                "Pinto",
                "Analytics",
                "Do it right",
                "oPinto@my_hosptital.rocks",
            ),
            (
                72,
                "Stefani-Schwab",
                "Stefani Schwab",
                "Stefani",
                "Schwab",
                "Analytics",
                "First at Work",
                "sSchwab@my_hosptital.rocks",
            ),
            (
                73,
                "Nereida-Minor",
                "Nereida Minor",
                "Nereida",
                "Minor",
                "Analytics",
                "Worker",
                "nMinor@my_hosptital.rocks",
            ),
            (
                74,
                "Kirby-Strother",
                "Kirby Strother",
                "Kirby",
                "Strother",
                "Analytics",
                "Worker",
                "kStrother@my_hosptital.rocks",
            ),
            (
                75,
                "Erinn-Spooner",
                "Erinn Spooner",
                "Erinn",
                "Spooner",
                "Analytics",
                "Worker",
                "eSpooner@my_hosptital.rocks",
            ),
            (
                76,
                "Youlanda-Driver",
                "Youlanda Driver",
                "Youlanda",
                "Driver",
                "Analytics",
                "Worker",
                "yDriver@my_hosptital.rocks",
            ),
            (
                77,
                "Ashlyn-Schulze",
                "Ashlyn Schulze",
                "Ashlyn",
                "Schulze",
                "Analytics",
                "Worker",
                "aSchulze@my_hosptital.rocks",
            ),
            (
                78,
                "Brianne-Lemmon",
                "Brianne Lemmon",
                "Brianne",
                "Lemmon",
                "Analytics",
                "Boss",
                "bLemmon@my_hosptital.rocks",
            ),
            (
                79,
                "Bebe-Ahern",
                "Bebe Ahern",
                "Bebe",
                "Ahern",
                "Analytics",
                "Worker",
                "bAhern@my_hosptital.rocks",
            ),
            (
                80,
                "Leigh-Bolen",
                "Leigh Bolen",
                "Leigh",
                "Bolen",
                "Ophthalmology",
                "Manager",
                "lBolen@my_hosptital.rocks",
            ),
            (
                81,
                "Shila-Pryor",
                "Shila Pryor",
                "Shila",
                "Pryor",
                "Ophthalmology",
                "Mr Cool",
                "sPryor@my_hosptital.rocks",
            ),
            (
                82,
                "Particia-Estrella",
                "Particia Estrella",
                "Particia",
                "Estrella",
                "Ophthalmology",
                "Do it right",
                "pEstrella@my_hosptital.rocks",
            ),
            (
                83,
                "Cheree-Seifert",
                "Cheree Seifert",
                "Cheree",
                "Seifert",
                "Ophthalmology",
                "First at Work",
                "cSeifert@my_hosptital.rocks",
            ),
            (
                84,
                "Christi-Lear",
                "Christi Lear",
                "Christi",
                "Lear",
                "Ophthalmology",
                "Worker",
                "cLear@my_hosptital.rocks",
            ),
            (
                85,
                "Dannie-Kenney",
                "Dannie Kenney",
                "Dannie",
                "Kenney",
                "Ophthalmology",
                "Worker",
                "dKenney@my_hosptital.rocks",
            ),
            (
                86,
                "Jarod-Tan",
                "Jarod Tan",
                "Jarod",
                "Tan",
                "Ophthalmology",
                "Worker",
                "jTan@my_hosptital.rocks",
            ),
            (
                87,
                "Alejandra-Bedard",
                "Alejandra Bedard",
                "Alejandra",
                "Bedard",
                "Orthopaedics",
                "Worker",
                "aBedard@my_hosptital.rocks",
            ),
            (
                88,
                "Jerrie-Joyce",
                "Jerrie Joyce",
                "Jerrie",
                "Joyce",
                "Orthopaedics",
                "Worker",
                "jJoyce@my_hosptital.rocks",
            ),
            (
                89,
                "Tiny-Rohr",
                "Tiny Rohr",
                "Tiny",
                "Rohr",
                "Orthopaedics",
                "Boss",
                "tRohr@my_hosptital.rocks",
            ),
            (
                90,
                "Donnetta-Grice",
                "Donnetta Grice",
                "Donnetta",
                "Grice",
                "Orthopaedics",
                "Worker",
                "dGrice@my_hosptital.rocks",
            ),
            (
                91,
                "Ruthanne-Cranford",
                "Ruthanne Cranford",
                "Ruthanne",
                "Cranford",
                "Orthopaedics",
                "Manager",
                "rCranford@my_hosptital.rocks",
            ),
            (
                92,
                "Annis-Turk",
                "Annis Turk",
                "Annis",
                "Turk",
                "Orthopaedics",
                "Mr Cool",
                "aTurk@my_hosptital.rocks",
            ),
            (
                93,
                "Ilona-Lassiter",
                "Ilona Lassiter",
                "Ilona",
                "Lassiter",
                "Orthopaedics",
                "Do it right",
                "iLassiter@my_hosptital.rocks",
            ),
            (
                94,
                "Daren-Ladd",
                "Daren Ladd",
                "Daren",
                "Ladd",
                "Orthopaedics",
                "First at Work",
                "dLadd@my_hosptital.rocks",
            ),
            (
                95,
                "Jenae-Woodbury",
                "Jenae Woodbury",
                "Jenae",
                "Woodbury",
                "Orthopaedics",
                "Worker",
                "jWoodbury@my_hosptital.rocks",
            ),
            (
                96,
                "Ashanti-Pritchett",
                "Ashanti Pritchett",
                "Ashanti",
                "Pritchett",
                "Orthopaedics",
                "Worker",
                "aPritchett@my_hosptital.rocks",
            ),
            (
                97,
                "Martina-Dawkins",
                "Martina Dawkins",
                "Martina",
                "Dawkins",
                "Orthopaedics",
                "Worker",
                "mDawkins@my_hosptital.rocks",
            ),
            (
                98,
                "Oma-Esposito",
                "Oma Esposito",
                "Oma",
                "Esposito",
                "Orthopaedics",
                "Worker",
                "oEsposito@my_hosptital.rocks",
            ),
            (
                99,
                "Carisa-Forbes",
                "Carisa Forbes",
                "Carisa",
                "Forbes",
                "Orthopaedics",
                "Worker",
                "cForbes@my_hosptital.rocks",
            ),
            (
                100,
                "Marti-Winter",
                "Marti Winter",
                "Marti",
                "Winter",
                "Orthopaedics",
                "Boss",
                "mWinter@my_hosptital.rocks",
            ),
        ]

        seed_user_role_links: list[tuple[str, int]] = [
            ("Hertha-Barham", 1),
            ("Hertha-Barham", 2),
            ("Amada-Tisdale", 2),
            ("Bryce-Bayne", 3),
            ("Hae-Weiner", 3),
            ("Shonda-Purcell", 4),
            ("Earle-Archuleta", 4),
            ("Garth-Cornwell", 5),
            ("Mardell-Crews", 5),
            ("Jade-Wiggins", 2),
            ("Marylee-Rauch", 2),
            ("Magda-Shook", 3),
            ("Nannie-Redmond", 3),
            ("Candance-Singer", 4),
            ("Renata-Bigelow", 4),
            ("Eve-Wilkinson", 5),
            ("Tiesha-Chavis", 5),
            ("Bernardine-Scherer", 2),
            ("Stefania-Wakefield", 2),
            ("Roselia-Hoskins", 3),
            ("Hyun-Rockwell", 3),
            ("Marcelina-Brinson", 4),
            ("Grazyna-Peter", 4),
            ("Yuko-Manley", 5),
            ("Lizzie-Olivas", 5),
            ("Theola-Blanchette", 2),
            ("Patrick-Watters", 2),
            ("Camila-Theriault", 3),
            ("Golda-Henke", 3),
            ("Alysia-Casteel", 4),
            ("Livia-Crayton", 4),
            ("Matilde-Alonzo", 5),
            ("Cleora-Parnell", 5),
            ("Willette-Marr", 2),
            ("Eddie-Pereira", 2),
            ("Evelin-Petersen", 3),
            ("Michaela-Mckeown", 3),
            ("Reyna-Blum", 4),
            ("Gail-Sapp", 4),
            ("Giselle-Sams", 5),
            ("Rhona-Whiting", 5),
            ("Merrill-Hirsch", 2),
            ("Vina-Winchester", 2),
            ("Ronnie-Nickerson", 3),
            ("Corrine-Landry", 3),
            ("Andrew-Janssen", 4),
            ("Fatimah-Sheehan", 4),
            ("Andrea-Rainey", 5),
            ("John-Knutson", 5),
            ("Andre-Meredith", 2),
            ("Dalene-Binkley", 2),
            ("Shaquana-Neeley", 3),
            ("Willy-Jarvis", 3),
            ("Dirk-Palma", 4),
            ("Raphael-Albers", 4),
            ("Kenya-Durham", 5),
            ("Nikole-Janes", 5),
            ("Nigel-Grove", 2),
            ("Wynona-Lancaster", 2),
            ("Delorse-Pence", 3),
            ("Claudie-Irwin", 3),
            ("Roxane-Moreau", 4),
            ("Jae-Clements", 4),
            ("Milagro-Montalvo", 5),
            ("Lang-Dowling", 5),
            ("Myles-Fulton", 2),
            ("Otelia-Bernstein", 2),
            ("Crystle-Homer", 3),
            ("Lawana-Herron", 3),
            ("Ollie-Pinto", 4),
            ("Stefani-Schwab", 4),
            ("Nereida-Minor", 5),
            ("Kirby-Strother", 5),
            ("Erinn-Spooner", 2),
            ("Youlanda-Driver", 2),
            ("Ashlyn-Schulze", 3),
            ("Brianne-Lemmon", 3),
            ("Bebe-Ahern", 4),
            ("Leigh-Bolen", 4),
            ("Shila-Pryor", 5),
            ("Particia-Estrella", 5),
            ("Cheree-Seifert", 2),
            ("Christi-Lear", 2),
            ("Dannie-Kenney", 3),
            ("Jarod-Tan", 3),
            ("Alejandra-Bedard", 4),
            ("Jerrie-Joyce", 4),
            ("Tiny-Rohr", 5),
            ("Donnetta-Grice", 5),
            ("Ruthanne-Cranford", 2),
            ("Annis-Turk", 2),
            ("Ilona-Lassiter", 3),
            ("Daren-Ladd", 3),
            ("Jenae-Woodbury", 4),
            ("Ashanti-Pritchett", 4),
            ("Martina-Dawkins", 5),
            ("Oma-Esposito", 5),
            ("Carisa-Forbes", 2),
            ("Marti-Winter", 2),
        ]

        seed_groups: list[tuple[str, str, str, str]] = [
            (
                "Accident and Emergency Group",
                "Accident and Emergency Group (Group)",
                "Accident_and_Emergency@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Admissions Group",
                "Admissions Group (Group)",
                "Admissions@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Cardiology Group",
                "Cardiology Group (Group)",
                "Cardiology@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Oncology Group",
                "Oncology Group (Group)",
                "Oncology@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Pharmacy Group",
                "Pharmacy Group (Group)",
                "Pharmacy@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Radiotherapy Group",
                "Radiotherapy Group (Group)",
                "Radiotherapy@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Urology Group",
                "Urology Group (Group)",
                "Urology@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Analytics Group",
                "Analytics Group (Group)",
                "Analytics@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Ophthalmology Group",
                "Ophthalmology Group (Group)",
                "Ophthalmology@my_hospital.rocks",
                "Email Distribution",
            ),
            (
                "Orthopaedics Group",
                "Orthopaedics Group (Group)",
                "Orthopaedics@my_hospital.rocks",
                "Email Distribution",
            ),
        ]

        with transaction.atomic(using=using):
            # Roles
            # The demo seed script assumes role IDs 1..5 exist.
            # Create placeholders if missing.
            role_defs = {
                1: ("Role 1", "Seed role 1"),
                2: ("Role 2", "Seed role 2"),
                3: ("Role 3", "Seed role 3"),
                4: ("Role 4", "Seed role 4"),
                5: ("Role 5", "Seed role 5"),
            }
            for role_id, (name, description) in role_defs.items():
                UserRoles.objects.using(using).get_or_create(
                    role_id=role_id, defaults={"name": name, "description": description}
                )

            role_admin = UserRoles.objects.using(using).get(role_id=1)
            role_user = UserRoles.objects.using(using).get(role_id=2)

            # Permissions
            perm_names = [
                "Create Collection",
                "Edit Collection",
                "Delete Collection",
            ]
            perms = {}
            for name in perm_names:
                perms[name], _ = RolePermissions.objects.using(using).get_or_create(
                    name=name, defaults={"description": name}
                )

            # Link permissions to roles
            for p in perms.values():
                RolePermissionLinks.objects.using(using).get_or_create(
                    role=role_admin, permission=p
                )
                RolePermissionLinks.objects.using(using).get_or_create(
                    role=role_user, permission=p
                )

            # Users (dbo.User) with stable IDs like the SQL seed script.
            conn = connections[using]
            with conn.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT dbo.[User] ON")
                for (
                    user_id,
                    username,
                    full_name,
                    first_name,
                    last_name,
                    department,
                    title,
                    email,
                ) in seed_users:
                    cursor.execute(
                        "SELECT 1 FROM dbo.[User] WHERE UserID = %s",
                        [user_id],
                    )
                    if cursor.fetchone() is not None:
                        continue

                    cursor.execute(
                        "INSERT INTO dbo.[User] (UserID, Username, FullName, FirstName, LastName, Department, Title, Email, DisplayName, Fullname_calc) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        [
                            user_id,
                            username,
                            full_name,
                            first_name,
                            last_name,
                            department,
                            title,
                            email,
                            full_name,
                            full_name,
                        ],
                    )
                cursor.execute("SET IDENTITY_INSERT dbo.[User] OFF")

            # UserRoleLinks (app.UserRoleLinks) by username -> roleId mapping
            for username, role_id in seed_user_role_links:
                user = AtlasUser.objects.using(using).get(username=username)
                role = UserRoles.objects.using(using).get(role_id=role_id)
                UserRoleLinks.objects.using(using).get_or_create(user=user, role=role)

            # Deterministic default user for the rest of the seed data.
            atlas_user = AtlasUser.objects.using(using).get(user_id=1)

            # UserGroups
            for account_name, group_name, group_email, group_type in seed_groups:
                Groups.objects.using(using).get_or_create(
                    name=group_name,
                    defaults={
                        "account_name": account_name,
                        "email": group_email,
                        "group_type": group_type,
                    },
                )

            # Memberships (match the seed script mapping by ranges)
            memberships: list[tuple[int, int]] = []
            memberships += [(u, 1) for u in range(1, 16)]
            memberships += [(u, 2) for u in range(16, 27)]
            memberships += [(u, 3) for u in range(27, 32)]
            memberships += [(u, 4) for u in range(32, 39)]
            memberships += [(u, 5) for u in range(39, 47)]
            memberships += [(u, 6) for u in range(47, 59)]
            memberships += [(u, 7) for u in range(59, 67)]
            memberships += [(u, 8) for u in range(67, 80)]
            memberships += [(u, 9) for u in range(80, 87)]
            memberships += [(u, 10) for u in range(87, 101)]

            for user_id, seed_group_num in memberships:
                user = AtlasUser.objects.using(using).get(user_id=user_id)
                group_name = seed_groups[seed_group_num - 1][1]
                group = Groups.objects.using(using).get(name=group_name)
                UserGroupMemberships.objects.using(using).get_or_create(
                    user=user, group=group
                )

            # Initiatives
            init, _ = Initiative.objects.using(using).get_or_create(
                name="Turbo Initiative",
                defaults={"description": "Seed initiative"},
            )

            # Terms
            term_columns, term_rows = _extract_insert_values_block("app.Term")
            term_insert_cols = ",".join(f"[{c}]" for c in term_columns)
            term_param_placeholders = ",".join(["%s"] * len(term_columns))
            conn = connections[using]
            with conn.cursor() as cursor:
                for row in term_rows:
                    name_idx = term_columns.index("Name")
                    cursor.execute(
                        "SELECT 1 FROM app.Term WHERE Name = %s",
                        [row[name_idx]],
                    )
                    if cursor.fetchone() is not None:
                        continue
                    cursor.execute(
                        f"INSERT INTO app.Term ({term_insert_cols}) VALUES ({term_param_placeholders})",
                        row,
                    )

            # ReportObject types are assumed pre-existing in Atlas, but the demo seed
            # references ReportObjectTypeID values. Ensure the referenced type IDs exist.
            # We intentionally keep names generic here.
            report_type_ids = {
                r[7]
                for r in _extract_values_list(
                    "insert into @SeedReportObjects", "IF COL_LENGTH('dbo.ReportObject'"
                )
            }
            for type_id in sorted(t for t in report_type_ids if t is not None):
                ReportObjectType.objects.using(using).get_or_create(
                    type_id=type_id,
                    defaults={"name": f"Type {type_id}", "short_name": "", "code": ""},
                )

            # ReportObject (dbo.ReportObject) with stable IDs 1..N (IDENTITY_INSERT)
            report_rows = _extract_values_list(
                "insert into @SeedReportObjects",
                "IF COL_LENGTH('dbo.ReportObject'",
            )

            with conn.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT dbo.ReportObject ON")
                for idx, row in enumerate(report_rows, start=1):
                    cursor.execute(
                        "SELECT 1 FROM dbo.ReportObject WHERE ReportObjectID = %s",
                        [idx],
                    )
                    if cursor.fetchone() is not None:
                        continue

                    (
                        report_object_biz_key,
                        source_server,
                        source_db,
                        source_table,
                        name,
                        description,
                        detailed_description,
                        report_object_type_id,
                        author_user_id,
                        last_modified_by_user_id,
                        last_modified_date,
                        report_object_url,
                        epic_master_file,
                        epic_record_id,
                        report_server_catalog_id,
                        default_visibility_yn,
                        orphaned_yn,
                        report_server_path,
                    ) = row

                    cursor.execute(
                        "INSERT INTO dbo.ReportObject ("
                        "ReportObjectID, ReportObjectBizKey, SourceServer, SourceDB, SourceTable, "
                        "Name, Description, DetailedDescription, ReportObjectTypeID, "
                        "AuthorUserID, LastModifiedByUserID, LastModifiedDate, ReportObjectURL, "
                        "EpicMasterFile, EpicRecordID, ReportServerCatalogID, DefaultVisibilityYN, "
                        "OrphanedReportObjectYN, ReportServerPath"
                        ") VALUES ("
                        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
                        ")",
                        [
                            idx,
                            report_object_biz_key,
                            source_server,
                            source_db,
                            source_table,
                            name,
                            description,
                            detailed_description,
                            report_object_type_id,
                            author_user_id,
                            last_modified_by_user_id,
                            last_modified_date,
                            report_object_url,
                            epic_master_file,
                            epic_record_id,
                            report_server_catalog_id,
                            default_visibility_yn,
                            orphaned_yn,
                            report_server_path,
                        ],
                    )
                cursor.execute("SET IDENTITY_INSERT dbo.ReportObject OFF")

            # Report docs
            doc_columns, doc_rows = _extract_insert_values_block("app.ReportObject_doc")
            doc_insert_cols = ",".join(f"[{c}]" for c in doc_columns)
            doc_param_placeholders = ",".join(["%s"] * len(doc_columns))
            with conn.cursor() as cursor:
                for row in doc_rows:
                    report_object_id = row[doc_columns.index("ReportObjectId")]
                    cursor.execute(
                        "SELECT 1 FROM app.ReportObject_doc WHERE ReportObjectId = %s",
                        [report_object_id],
                    )
                    if cursor.fetchone() is not None:
                        continue
                    cursor.execute(
                        f"INSERT INTO app.ReportObject_doc ({doc_insert_cols}) VALUES ({doc_param_placeholders})",
                        row,
                    )

            # Report term links
            report_term_pairs = _extract_values_list_in_section(
                "insert into app.ReportObjectDocTerms",
                ") v(ReportObjectID, TermId)",
            )
            for report_object_id, term_id in report_term_pairs:
                if (
                    not ReportObjectDocTerms.objects.using(using)
                    .filter(
                        report_doc_id=report_object_id,
                        term_id=term_id,
                    )
                    .exists()
                ):
                    ReportObjectDocTerms.objects.using(using).create(
                        report_doc_id=report_object_id,
                        term_id=term_id,
                    )

            # Report doc fragility tags
            fragility_tag_pairs = _extract_values_list_in_section(
                "insert into app.reportobjectdocfragilitytags",
                ") v(ReportObjectID, FragilityTagID)",
            )
            for report_object_id, fragility_tag_id in fragility_tag_pairs:
                if (
                    not ReportObjectDocFragilityTags.objects.using(using)
                    .filter(
                        report_doc_id=report_object_id,
                        fragility_tag_id=fragility_tag_id,
                    )
                    .exists()
                ):
                    ReportObjectDocFragilityTags.objects.using(using).create(
                        report_doc_id=report_object_id,
                        fragility_tag_id=fragility_tag_id,
                    )

            # Report hierarchy
            hierarchy_pairs = _extract_values_list_in_section(
                "insert into dbo.ReportObjectHierarchy",
                ") v(ParentReportObjectID, ChildReportObjectID)",
            )
            for parent_id, child_id in hierarchy_pairs:
                ReportObjectHierarchy.objects.using(using).get_or_create(
                    parent_report_id=parent_id,
                    child_report_id=child_id,
                )

            # Maintenance logs (the legacy seed uses a temp table and then inserts into app.MaintenanceLog,
            # sometimes via dynamic FK detection. We seed deterministically by attaching logs to the
            # lowest existing ReportObject_doc id.
            maintenance_rows = _extract_values_list(
                "insert into #SeedMaintenanceLog",
                "declare @MaintenanceLogFkColumn",
            )

            lowest_doc_id = (
                ReportObjectDocTerms.objects.using(using)
                .order_by("report_doc_id")
                .values_list("report_doc_id", flat=True)
                .first()
            )
            if lowest_doc_id is None:
                lowest_doc_id = 1

            for maintainer_id, maintenance_date, comment, status_id in maintenance_rows:
                if (
                    not MaintenanceLog.objects.using(using)
                    .filter(
                        report_doc_id=lowest_doc_id,
                        maintainer_id=maintainer_id,
                        maintenance_date=maintenance_date,
                        comment=comment,
                        status_id=status_id,
                    )
                    .exists()
                ):
                    ml = MaintenanceLog.objects.using(using).create(
                        report_doc_id=lowest_doc_id,
                        maintainer_id=maintainer_id,
                        maintenance_date=maintenance_date,
                        comment=comment,
                        status_id=status_id,
                    )
                    ReportObjectDocMaintenanceLogs.objects.using(using).get_or_create(
                        report_doc_id=lowest_doc_id,
                        maintenance_log_id=ml.maintenance_log_id,
                    )

            # Report queries
            query_pairs = _extract_values_list(
                "insert into #SeedReportObjectQuery (ReportObjectKey, Query) values",
                "if col_length('dbo.ReportObjectQuery'",
            )
            for report_object_id, query in query_pairs:
                ReportObjectQuery.objects.using(using).get_or_create(
                    report_id=report_object_id,
                    query=query,
                )

            # Report run data
            run_rows = _extract_values_list(
                "insert into #SeedReportObjectRunData",
                "if col_length('dbo.ReportObjectRunData'",
            )

            with conn.cursor() as cursor:
                for (
                    report_object_key,
                    run_id,
                    run_user_id,
                    run_start_time,
                    run_dur,
                    run_status,
                ) in run_rows:
                    run_data_id = str(run_id)
                    cursor.execute(
                        "SELECT 1 FROM dbo.ReportObjectRunData WHERE RunDataId = %s",
                        [run_data_id],
                    )
                    if cursor.fetchone() is not None:
                        continue
                    cursor.execute(
                        "INSERT INTO dbo.ReportObjectRunData "
                        "(RunDataId, RunUserID, RunStartTime, RunDurationSeconds, RunStatus) "
                        "VALUES (%s,%s,%s,%s,%s)",
                        [run_data_id, run_user_id, run_start_time, run_dur, run_status],
                    )
                    cursor.execute(
                        "INSERT INTO dbo.ReportObjectRunDataBridge (ReportObjectId, RunId, Runs, Inherited) "
                        "SELECT %s, %s, 1, 'N' "
                        "WHERE NOT EXISTS (SELECT 1 FROM dbo.ReportObjectRunDataBridge WHERE ReportObjectId=%s AND RunId=%s)",
                        [report_object_key, run_id, report_object_key, run_id],
                    )

            # Favorites
            fav_columns, fav_rows = _extract_insert_values_block(
                "app.UserFavoriteFolders"
            )
            fav_insert_cols = ",".join(f"[{c}]" for c in fav_columns)
            fav_param_placeholders = ",".join(["%s"] * len(fav_columns))
            with conn.cursor() as cursor:
                for row in fav_rows:
                    folder_name = row[fav_columns.index("FolderName")]
                    user_id = row[fav_columns.index("UserId")]
                    cursor.execute(
                        "SELECT 1 FROM app.UserFavoriteFolders WHERE FolderName=%s AND UserId=%s",
                        [folder_name, user_id],
                    )
                    if cursor.fetchone() is not None:
                        continue
                    cursor.execute(
                        f"INSERT INTO app.UserFavoriteFolders ({fav_insert_cols}) VALUES ({fav_param_placeholders})",
                        row,
                    )

            # Tags
            tag, _ = Tag.objects.using(using).get_or_create(
                name="seed", defaults={"description": "Seed tag"}
            )

            # Collection
            collection, _ = Collection.objects.using(using).get_or_create(
                name="Getting Started",
                defaults={
                    "initiative": init,
                    "search_summary": "Seed collection",
                    "description": "Welcome to Turbo",
                    "modified_by": atlas_user,
                    "hidden": "N",
                },
            )

            CollectionReport.objects.using(using).get_or_create(
                collection=collection,
                report_id=1,
                defaults={"rank": 0},
            )

        self.stdout.write(self.style.SUCCESS("dg_db seed complete"))
