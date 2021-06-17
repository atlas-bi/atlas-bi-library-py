# 1 remove old report records from solr
# reports
# initiatives
# projects
# terms
# users

# for report_type in ['reports','initiatives','projects','terms','users']:
#     print(report_type)
#     print(solr.search(
#         "*:*",
#         fq="type:%s" % report_type,
#         fl="atlas_id",
#         start = 0,
#         rows=0).hits)
