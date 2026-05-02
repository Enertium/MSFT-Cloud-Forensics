TODO
====



BECAUSE forensic dumps must be strictly reproducible:

MUST normalize photo metadata in existing dump files by removing orientationV2 field and converting "orientation" string values to numeric (e.g. "6" → 6) in photo.orientation field BECAUSE orientation metadata varies between Graph API versions and mixed string/numeric values break idempotency.
MUST modify OneDriveAutomation metadata processing to normalize photo.orientation values to numeric format and exclude orientationV2 field during file capture BECAUSE this ensures consistent metadata format regardless of Graph API version and prevents false positive diffs between dumps taken at different times.

Test #1:

tail -n +8 20241113-ap@vizdynamics.com-Business-list.txt | head -n 100 > old.tmp
tail -n +8 20250131-ap@vizdynamics.com-Business.list.txt | head -n 100 > new.tmp
diff -U 3 old.tmp new.tmp

Test #2:

sed 's/"orientation": "6"/"orientation": 6/g' 20241113-ap@vizdynamics.com-Business-list.txt | sed 's/, "orientationV2": 6//g' > 20241113-ap@vizdynamics.com-Business.list.txt.tmp
sed 's/"orientation": "6"/"orientation": 6/g' 20250131-ap@vizdynamics.com-Business.list.txt | sed 's/, "orientationV2": 6//g' > 20250131-ap@vizdynamics.com-Business.list.txt.tmp
diff -U 3 20241113-ap@vizdynamics.com-Business.list.txt.tmp 20250131-ap@vizdynamics.com-Business.list.txt.tmp | head -n 50

Test #3:

tail -n +8 20241113-ap@vizdynamics.com-Business-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250131-ap@vizdynamics.com-Business.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp


tail -n +8 20241113-ap@vizdynamics.com-Personal-list.txt | ../make_comparable.py | sort > old.comparable.tmp
tail -n +8 20250131-ap@vizdynamics.com-Personal.list.txt | ../make_comparable.py | sort > new.comparable.tmp
diff old.comparable.tmp new.comparable.tmp


diff -y --suppress-common-lines old.comparable.tmp new.comparable.tmp | more




Testing goals:

BECAUSE forensic comparability must be guaranteed:
- MUST detect any real file system changes between dumps
- MUST NOT flag false positives from API metadata variations
- MUST preserve all essential cloud state fields for forensic analysis

