# NEWS! IMPORTANT!
If you have no data in your cores after getting the latest version, you need to run the (top-level) "dbconversion.py" script. Run this exactly as you do cscience.py; you will need to have mongodb up and running when you do. After this has run, you can re-open cscience.py and your data should appear as normal.

# CSciBox
CSciBox is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

The project webpage is here:  [**CSciBox Webpage**](http://www.cs.colorado.edu/~lizb/cscience.html), and includes more detailed information about the project and a simple tutorial.

There are two options for those who want to use the software.

1. One step installer (**recommended for most users**)
2. Development Installation (for those who want to work with the source code)

Details on both options are found below.

## One-Step Installer (recommended for most users)

There is an installer (OSX and Windows) available here: [**CSciBox Releases**](https://github.com/ldevesine/Calvin/releases)

Currently CSciBox has been tested on OSX 10.9 (Mavericks) and there is a separete release for OSX 10.7 and 10.8 (Lion and Mountain Lion)

Please send your email address to lizb@colorado.edu so that we can keep you informed of future updates and get any feedback you may have.

The only requirement for Mac is to be running OSX 10.6 (Snow Leopard) or greater. You do not need to install python or any packages when using the packaged release.

Windows executable is 32-bits, and can be run as a stand-alone executable, no installation is necessary.

## Development (Only if you like getting your hands dirty)
In development, this project depends on the following packages.  Installing them in this order
will likely reduce your unhappiness:

1. [Python 2.7](https://www.python.org/downloads/)

2. [wxPython](http://www.wxpython.org/download.php) -- currently tested against version 3.0.0.0, Used for the GUI

3. [scipy/numpy/matplotlib](http://www.scipy.org/install.html) -- follow link for instructions on installation, Used for calculations and plotting

4. [pymongo 2.8](http://api.mongodb.org/python/current/installation.html) (install using: `pip install pymongo==2.8`) -- Database for storage of all data

5. [quantities](https://pypi.python.org/pypi/quantities) -- Used for handling engineering units

6. [bagit](http://libraryofcongress.github.io/bagit-python/) -- Used for exporting data

Note that you will also need access to a running mongodb server.
After you have started up your local mongodb server, you should populate it with initial data by
using the mongorestore command (see [mongodb manual -- mongorestorre]( http://docs.mongodb.org/manual/reference/program/mongorestore/))
and the data stored in this repository at `database_dump/dump/repository`. This will give you a set
of initial (public) data to work from.

CSciBox contains a number of code modules that were written by others:

- Bacon http://chrono.qub.ac.uk/blaauw/bacon.html

If you want to use Bacon, you need the compiled version.  You may need
to run the appropriate makefile in the `src/plugins/bacon` directory of
this distribution to produce that file.  This will create a directory
in `src/plugins/bacon` called pluginfiles.  Move the contents of that directory
to `src/cscience/components/cfiles`.

- StratiCounter https://github.com/maiwinstrup/StratiCounter

If you want to use StratiCounter, you'll need to download the Matlab
2014b runtime available [here](http://www.mathworks.com/products/compiler/mcr/)

Although the installation instructions above focus on using a local mongodb server for data storage,
it is possible to use CScience with a remote mongodb installation or with hbase. To use a remote
mongodb server, edit the `db_location` and `db_port` variables in the `src/config.py` file to point to
your remote database. To run against an hbase server, you will also need to install the happybase
python package and change the `db_type` variable to `hbase`.
