# limonada
LIpid Membranes Open Network And DAtabase


__Installation__

This project requires Python 3.9 or earlier.

1. git clone https://github.com/LimonadaMD/LimonadaMD.git
2. python3 -m pip install numpy
3. pip install -r requirements/dev.txt
4. apt-get install sqlite3 openbabel
5. sqlite3 db.sqlite3 < db.sqlite3.txt
6. python manage.py migrate
7. python manage.py runserver

__Configuration__

When a topology is added to the database, a verification is made with gromacs or charmm to check its validity.
Add gromacs and charmm bin path at the end of limonada/settings/base.py

Add a cron task to remove temporary files created in the media/tmp directory
  Change the media path in limonada.cron
  copy limonada.cron to /usr/bin/
  execute "crontab -e" and add "0 * * * * /usr/bin/limonada.cron" at the end of the file


