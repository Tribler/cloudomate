==========
Cloudomate
==========



.. image:: https://jenkins.tribler.org/buildStatus/icon?job=pers/Cloudomate
   :target: https://jenkins.tribler.org/job/pers/job/Cloudomate/
   :alt: Build Status

.. image:: https://files.slack.com/files-pri/T546HRL3H-F5KQ13400/cloudomate-logo.png?pub_secret=1234824941
   :alt: Cloudomate logo

Overview
========

Cloudomate is an unpermissioned open compute API which provides an automated way to buy VPS instances from multiple providers. The easiest way to use Cloudomate is via the command-line interface. 

Requirements
============

* Python 2.7
* python-lxml installed on the system
* Works on Linux, Mac OSX, BSD
* An active Electrum_ wallet with sufficient funds

Installation
============

The project can be install through the following commands ::

   git clone https://github.com/Jaapp-/cloudomate.git
   cd cloudomate
   pip install .


Providers
=========

Currently the following VPS providers are implemented: ::

   linevast       https://linevast.de/
   pulseservers   https://pulseservers.com/
   rockhoster     https://rockhoster.com/
   blueangelhost  https://www.blueangelhost.com/
   ccihosting     http://www.ccihosting.com/
   crowncloud     http://crowncloud.net/

This same list can be accessed through the list command. ::

   cloudomate list


Configuration
-------------

For some commands, mainly purchase, user configuration is required. The
main way to do this is through a configruation file. For Linux, the default
location for the configuration file is `$HOME/.config/cloudomate.cfg`.

A configuration file looks like this ::

   [User]
   email = 
   firstName = 
   lastName = 
   companyName = 
   phoneNumber = 
   password = 

   [Address]
   address = 
   city = 
   state = 
   countryCode = 
   zipcode = 

   [Server]
   rootpw = 
   ns1 = 
   ns2 = 
   hostname = 


Section can be overridden for specific providers by adding a section,
for example a [rockhoster] section can contain a separate email address only
to be used for RockHoster.


Basic usage
-----------

::

   usage: cloudomate [-h] {list,options,purchase,status,setrootpw,getip} ...

   Cloudomate

   positional arguments:
     {list,options,purchase,status,setrootpw,getip}
       list                List providers
       options             List provider configurations
       purchase            Purchase VPS
       status              Get the status of the services.
       setrootpw           Set the root password of the last activated service.
       getip               Get the ip of the specified service.

   optional arguments:
     -h, --help            show this help message and exit


options
-------

List the options for RockHoster_ ::
    
    
    $ cloudomate options rockhoster

::
    
    Options for rockhoster:

      #    Name              CPU (cores)       RAM (GB)          Storage (GB)      Bandwidth (TB)    Connection (Mbps) Estimated Price (mBTC)
      0    Basic              1                1                 25                unmetered         500               3.47
      1    Premium            2                2                 50                unmetered         500               5.27
      2    Expert             3                4                 100               unmetered         500               9.3
      3    Maximum            4                8                 150               unmetered         500               16.25
      4    Basic              2                1                 40                unmetered         1000              5.27
      5    Premium            2                2                 80                unmetered         1000              8.41
      6    Expert             3                4                 150               unmetered         1000              14.23
      7    Maximum            4                8                 300               unmetered         1000              24.54


Purchase
--------

Use the purchase command to purchase a VPS instance. An account is created
and the instance is paid through an Electrum wallet. ::
   
   $ cloudomate purchase rockhoster 0
  
::

   Selected configuration:
   Name           CPU            RAM            Storage        Bandwidth      Est.Price
   Basic          1              1.0            25.0           unmetered      4.99
   Purchase this option? (y/N)

Manage
------

The following functions can be used to manage a purchased VPS instances ::

    status              Get the status of the services.
    setrootpw           Set the root password of the last activated service.
    getip               Get the ip of the specified service.



Tests
=====

To run the project's tests   ::
    
    python -m unittest discover



.. _RockHoster: https://rockhoster.com/
.. _Electrum: https://electrum.org/
