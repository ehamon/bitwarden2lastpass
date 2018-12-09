# Bitwarden2Lastpass.py

**Bitwarden2Lastpass.py** is a free software (GNU GPL3 license) that allows to easily convert a CSV file exported from the password manager [Bitwarden](https://vault.bitwarden.com/) to a CSV file in[Lastpass] format (https://lastpass.com/).

# Installation
* copy file '**bitwarden2lastpass.py**' in ~/local/bin or in /usr/local/bin (root is required in this case)

# Dépendencies

* python 3.7
* pip install csv errno getopt inspect ntpath os pathlib platform re logging sys


# KDE integration

See the video [bitwarden2lastpass-kde-dolphin-integration.mp4](https://youtu.be/pdnUDLsNxMc)

* Edit and adapt the files to your installation:
  * bitwarden2lastpass.bash
  - bitwarden2lastpass.desktop
* Copy *bitwarden2lastpass.bash* in *~/local/bin* or in */usr/local/bin*
* run **kf5-config --path services** to determine repositories
      ~/.local/share/kservices5/ServiceMenus/
    and
      /usr/share/kservices5/ServiceMenus/
* cp bitwarden2lastpass.desktop ~/.local/share/kservices5/ServiceMenus/
* Close all instances of **Dolphin** in your session **KDE**.
* Et voilà.


# Usage

  **python bitwarden2lastpass.py --help**

```
  bitwarden2lastpass.py -i <inputfile> -o <outputfile> -d <directory>
  bitwarden2lastpass.py.

  Usage:
    bitwarden2lastpass.py
           detect the last bitwarden exxport file in the current directory and convert it to a compatible lastpass export file.
           (same to 'bitwarden2lastpass.py -d .')
    bitwarden2lastpass.py -d <directory>
           detect the last bitwarden exxport file in the directory <directory> and convert it to a compatible lastpass export file.
    bitwarden2lastpass.py -i <export-bitwarden-file>
           convert <export-bitwarden-file> to a compatible lastpass export file, in the same directory.
    bitwarden2lastpass.py -i <export-bitwarden-file> -o <export-lastpass-file>
           convert <export-bitwarden-file> to a compatible lastpass export file with name : <export-lastpass-file>
    bitwarden2lastpass.py (-h | --help)
    bitwarden2lastpass.py --version

  Options:
    -h --help     Show this screen.
    -v --version  Show version.

```


# Other

More information on my blog: [ehamon.fr](https://ehamon.fr/posts/20181209/bitwarden2lastpass-un-convertisseur-csv-de-bitwarden-vers-lastpass/)
