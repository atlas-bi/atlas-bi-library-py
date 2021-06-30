..
    Atlas of Information Management
    Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

******
Deploy
******

#################
Setup Solr Search
#################


Atlas uses two Solr Cores

* atlas
* atlas_lookups


Create the cores

..  code::

    solr create -c atlas
    solr create -c atlas_lookups


If you're rather use different names for the cores, it is no problem, as long as you update the core name in Atlas settings.

#############
Deploy to IIS
#############

.. tab:: Deploy With Visual Studio

   Deploying with Visual Studio is the preferred method. After opening the ``web.sln`` file -

   - First update ``web/appsettings.json`` with the correct settings for your database and organization.
   - In Visual Studio's menu, click **Build** then **Publish Web**
   - Create a new publish profile.

     - Choose **Web Server (IIS)** as the **Target**
     - Choose **Web Deploy** as the **Specific target**
     - Enter your IIS **Server** name
     - Enter your **Site name**. This must match the site name already created on the web server (``atlas-dev``)
     - Enter the web url in **Destination URL**
     - Optionally enter you credentials for the web server

   - After the profile is created click **Edit** to change additional settings.
   - Change to the **Settings** tab and change the **Target Runtime** to match the web servers .NET bitness.

     .. list-table::

        * - .. figure:: ../images/deploy/vs_profile.png
               :alt: Edit publish profile

   - In order to successfully publish the connection must be validated to allow self-signed certificates.

     .. list-table::

        * - .. figure:: ../images/deploy/vs_connection.png
               :alt: Validate connection
        * - .. figure:: ../images/development/ssl_warning.png
               :alt: ssl warning
        * - .. figure:: ../images/development/ssl_confirm.png
               :alt: ssl confirm


     .. attention::
        The connection must be re-verified every time Visual Studio is restarted.

   - Finally publish Atlas by clicking **Publish** button.

     .. list-table::

        * - .. figure:: ../images/deploy/vs_publish.png
               :alt: Publish Atlas

.. tab:: Manually Deploy

   Atlas is fairly simple to manually deploy.

   - First pull Atlas's source code onto the server
   - Update ``web/appsettings.json`` with the correct settings for your database and organization.
   - Run dotnet publish from the ``web`` folder to build the Atlas runtime.

     .. code:: sh

        dotnet publish -r win-x86 --self-contained false -c Release -o out

     .. attention::
        Ensure the bitness matches the bitness of the .NET version you've installed on the server!

   - Copy the contents of the newly created ``out`` directory into the ``c://inetpub/wwwroot/atlas-dev`` folder.

   **Navigate to your binding and Atlas should be available!**
