# INTRODUCTION

𝗦.𝗧. 𝗖𝗟𝟬𝗪𝗗 𝗙𝗢𝗥𝗘𝗡𝗦𝗜𝗖𝗦 𝗜𝗦 𝗧𝗛𝗘 𝗡𝗘𝗪 𝗡𝗘𝗪 𝗧𝗛𝗜𝗡𝗚
Got problems with #cl0wd / #cloud files going missing, and can't keep backups in your house? Well start collecting evidence: Announcing #CloudForensics.

Use this before #CIA #McKinsey the "#TimeBombCEOFactory" (TM) T/a D.B.A MICROSOFT CORPORATION (now with a #Mckinseyite CEO! OH NO!!) nukes your entire existence out of existence by "oh woops" making your E3/E5 SharePoint files go into full "FUCK YOU FUCK OFF PARTNERS PROGRAM" (TM) mode [sic], and then your company doesn't exist. 

Or before your local #PoliceMilitarization #CommunistUnions police start to raid your files and delete from existence anything they like for the strangest and most obvious of reasons: Facism, and Intellectual Property theft. If you don't already know, they do have access to your entire cloud. All of the clouds. Always. With no oversight or security controls (FR). Yes, I hate to tell you: this is actually a thing. Welcome to #FusionCenters and the #NewWorldOrder, in 2026.

Run this regularly to keep track of lost/missing/damaged files on #OneDrive, #O365 + E3/E5 #SharePoint. Use this to keep track of your files. It's diff-able. Enterprise & Personal. All of $MSFT #MSFT #Microsoft #MicrosoftCorporation cl0wd. #CloudForensics.

# TECHNICAL SUPPORT

Please use Discussions here for technical support. See:
https://github.com/Enertium/MSFT-Cloud-Forensics/discussions

For more hot tips on Cyber Security and Physical Security in these dystopian times, take a look at my Physical Security tips on APMonitor.PY here:

https://github.com/CompSciFutures/APMonitor#recommended-configurations-for-addressing-the-first-pillar-physical-security

And the BeerIsGood Security & Privacy links collection is also rather decent:

https://github.com/beerisgood/Security-link-collection

# BASIC INSTRUCTIONS / EXAMPLE

# Setup Your Azure Appliation

See "Setting up client_id, client_secret & tenant_id:" in download_metadata.py for instructions on how to setup <client_id> / <client_secret>

# Put your client secrets into download_metadata.py:

> # CHANGE THESE TO YOUR AZURE APPLICATION:
> # See "Setting up client_id, client_secret & tenant_id:" below for instructions on how to setup <client_id> / <client_secret>
> # e...v@gmail.com
> CLIENT_ID = "<YOUR CLIENT_ID>",
> CLIENT_SECRET = "<YOUR CLIENT_SECRET>"

# Activate the Python Virtual Environment

source /home/ap/workspaces/admin-scripts/OneDriveAutomation/.venv/bin/activate

# Run the script

cd ~/workspaces/admin-scripts/OneDriveAutomation/OneDriveDumps
python3 ../download_metadata.py > output.txt
** login to account w/ browser
keep the console log: cat << ++ > 20250131-ap@vizdynamics.com-Business.log.txt
rename the output file: mv output.txt 20250131-ap@vizdynamics.com-Business.list.txt

# Compare the output

tail -n +8 20241113-ap@vizdynamics.com-Business-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250131-ap@vizdynamics.com-Business.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20241113-ap@vizdynamics.com-Personal-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250131-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20241113-ap@vizdynamics.com-Personal-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250131-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20241113-ap@vizdynamics.com-Personal-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250223-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20241113-ap@vizdynamics.com-Business-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250223-ap@vizdynamics.com-Business.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20250223-ap@vizdynamics.com-Business.list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250322-ap@vizdynamics.com-Business.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20250223-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250322-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

tail -n +8 20250322-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250929-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp

Good luck! And bump me on the "Discussions" forum in the navbar above if you have problems.

Andrew (AP) Prendergast
https://linktr.ee/CompSciFutures
Master of Science

Ex-ServerMasters
Ex-Googler
Ex-Xerox PARC/PARK
Ex-Intel Foundry
Ex Chief Scientist @ Clemenger BBDO / Omnicom

ACM, IEEE & INFORMS member.


