# VOiC

<!-- - Create a **'.env'** file in the root directory and add the following environment variables:

    - **SECRET_KEY**: your secret key
    - **MAIL_USERNAME**: your Outlook email address
    - **MAIL_PASSWORD**: your Outlook account password
    
    - **DB_HOST**: the hostname or IP address of your database server
    - **DB_USER**: the username for your database
    - **DB_PASSWORD**: the password for your database
    - **DB_NAME**: the name of your database
    
    - **RECAPTCHA_PUBLIC_KEY**: the public key for your reCAPTCHA account
    - **RECAPTCHA_PRIVATE_KEY**: the private key for your reCAPTCHA account
    
    

-Import from **'requirements.txt'**

    -pip install -r requirements.txt -->


VOiC requires many setup steps to properly function.  Developers should be capable of using a bash terminal as it is required for many installation steps.  A Unix-based operating system, preferably a Debian Linux distribution, is the suggested method, but Windows Subsystem Linux (WSL) is also acceptable to.  Now you will want to install python3 by open up a bash terminal, using the following command to install the python3 package.

>  $sudo apt install python3

You will also want a similar command to install pip3. This will allow you to install the required python libraries.

>  $sudo apt install python3-pip

Now you will need to clone the git repository to your local machine.  If you don't have git, you will need to install that package.

>  $ sudo apt install git

>  $ git clone https://github.com/ConnerWiench/VOiC.git

We will now use move into the cloned repository and use the 'requirements.txt' file to download all required python libraries to install VOiC.

>  $ cd VOiC

>  $ pip3 install -r requirements.txt

Once all the libraries finish installing, you will need to create a database and user that has access to the database.  Start by installing the MySQL client. Version 8.0 is suggested.

>  $ sudo apt install mysql-client-8.0

We will need to first log in to the mysql client using the root user.  From here we may create the VOiC database and user.

>  $ sudo mysql

You can use the following two commands in the mysql terminal to create the database and user.  Replace the \<password\> field with your desired password.

>  mysql> CREATE DATABASE voic_db;

>  mysql> CREATE USER 'voic'@'localhost' IDENTIFIED
>         WITH authentication_plugin BY '\<password\>';

Now we will grant the voic user all priveledges to the voic\_db database.

>  mysql> GRANT ALL PRIVELEDGES ON voic_db
>         TO 'voic'@'localhost';

Either as root user or the voic user, you can not format the database required by VOiC.  Begin by opening the voic\_db, then pasting in the contents of the latest version of sql file found in the backend folder of the repository.

>  mysql> USE voic_db;
>  mysql> \<Paste contents of .sql file here\>

With the information used to create the database user, we will now create the .env file to allow the application to access required resources.  In the same step we will setup the email in the .env file as it is needed for the reset password process.  Create a .env file in the frontend directory and add the following fields  You can create a reCaptcha key on [Google Projects](https://console.cloud.google.com/projectselector2/security/recaptcha:).

>  SECRET_KEY=\<session key (can be anything)\>

>  MAIL_USERNAME=\<email@domain.com\>

>  MAIL_PASSWORD=\<email password\>

>  DB_HOST=localhost

>  DB_USER=voic

>  DB_PASSWORD=\<user password\>

>  DB_NAME=voic_db

>  RECAPTCHA_PUBLIC_KEY=\<public key\>

>  RECAPTCHA_PRIVATE_KEY=\<private key\>

Updated the information to what you set it as in the earlier steps.  You should only need to change the user, and the password.
Everything is now setup for VOiC to function.  To startup the development server, execute the app.py in the frontend  directory file.

>  $ python3 app.py