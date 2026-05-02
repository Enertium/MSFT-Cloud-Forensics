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


