# Introduction

𝗦.𝗧. 𝗖𝗟𝟬𝗪𝗗 𝗙𝗢𝗥𝗘𝗡𝗦𝗜𝗖𝗦 𝗜𝗦 𝗧𝗛𝗘 𝗡𝗘𝗪 𝗡𝗘𝗪 𝗧𝗛𝗜𝗡𝗚

Got problems with #cl0wd / #cloud files going missing, and can't keep backups in your house? Well start collecting evidence: Announcing #CloudForensics.

Run this regularly to keep track of lost/missing/damaged files on #OneDrive, #O365 + E3/E5 #SharePoint. Use this to keep track of your files. It's diff-able. Enterprise & Personal. All of $MSFT #MSFT #Microsoft #MicrosoftCorporation cl0wd. #CloudForensics.

Use this before #CIA #McKinsey the "#TimeBombCEOFactory" (TM) a #CommunistUnions subsidiary of "#NationalSecurityCouncil" #NSC (TM) T/a D.B.A MICROSOFT CORPORATION (now with a #Mckinseyite CEO! OH NO!!) nukes your entire existence out of existence by "oh woops" making your E3/E5 SharePoint files go into full "FUCK YOU FUCK OFF PARTNERS PROGRAM" (TM) mode [sic], and then your company doesn't exist.

See this X post for a date when it got really really bad for alot of people in Advertising and Tech:
https://x.com/CompSciFutures/status/1975555792880439517?s=20

Or. Use this before your local #PoliceMilitarization #CommunistUnions police start to raid your files and delete from existence anything they like for the strangest and most obvious of reasons: Facism, and Intellectual Property theft. If you don't already know, they do have access to your entire cloud. All of the clouds. Always. With no oversight or security controls (FR). Yes, I hate to tell you: this is actually a thing. Welcome to #FusionCenters and the #NewWorldOrder, in 2026.

I'll say it again:
Run this regularly to keep track of lost/missing/damaged files on #OneDrive, #O365 + E3/E5 #SharePoint. Use this to keep track of your files. It's diff-able. Enterprise & Personal. All of $MSFT #MSFT #Microsoft #MicrosoftCorporation cl0wd. #CloudForensics.

Good luck! And bump me on the "Discussions" forum in the navbar above if you have problems.

[![buy-me-a-coffee.png](images/buy-me-a-coffee.png)](https://www.paypal.com/donate/?hosted_button_id=WN472NX5XC5CJ)

Andrew (AP) Prendergast<br />
https://linktr.ee/CompSciFutures<br />
Master of Science<br/>

Ex-ServerMasters<br/>
Ex-Googler<br/>
Ex-Xerox PARC/PARK<Br/>
Ex-Intel Foundry<br/>
Ex Chief Scientist @ Clemenger BBDO / Omnicom<br/>

ACM, IEEE & INFORMS member.<br/>

# Technical Support

Please use Discussions here for technical support. See:
https://github.com/Enertium/MSFT-Cloud-Forensics/discussions

For more hot tips on Cyber Security and Physical Security in these dystopian times, take a look at my Physical Security tips on APMonitor.PY here:

https://github.com/CompSciFutures/APMonitor#recommended-configurations-for-addressing-the-first-pillar-physical-security

And the BeerIsGood Security & Privacy links collection is also rather decent:

https://github.com/beerisgood/Security-link-collection

# Basic Instructions / Example

## Setup Your Azure Appliation

See "Setting up client_id, client_secret & tenant_id:" in download_metadata.py for instructions on how to setup <client_id> / <client_secret>

## Put your client secrets into download_metadata.py:

> # CHANGE THESE TO YOUR AZURE APPLICATION:
> # See "Setting up client_id, client_secret & tenant_id:" below for instructions on how to setup <client_id> / <client_secret>
>
> ```
> CLIENT_ID = "<YOUR CLIENT_ID>",
> CLIENT_SECRET = "<YOUR CLIENT_SECRET>"
> ```

## Activate the Python Virtual Environment

```
source /home/ap/workspaces/admin-scripts/OneDriveAutomation/.venv/bin/activate
```

## Run the script

```
cd ~/workspaces/admin-scripts/OneDriveAutomation/OneDriveDumps
python3 ../download_metadata.py > output.txt
** login to account w/ browser
keep the console log: cat << ++ > 20250131-ap@vizdynamics.com-Business.log.txt
rename the output file: mv output.txt 20250131-ap@vizdynamics.com-Business.list.txt
```

## Compare the output

```
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
```
# Setting Up `client_id`, `client_secret` & `tenant_id`

## 1. Create a New App Registration

1. Go to the [Azure Portal](https://portal.azure.com)
2. Search for and select **Azure Active Directory** (or **Microsoft Entra ID** in newer portals)
3. In the left menu, click **App registrations**
4. Click **+ New registration** and fill in the following:
   - **Name:** `OneDriveAutomation` (or your preferred name)
   - **Supported account types:** *Accounts in any organizational directory (Any Azure AD directory – Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)*
   - **Redirect URI:** Select **Web** and enter `http://localhost:8000`
5. Click **Register**

## 2. Note Your IDs

On the next screen, copy the following values:

| Field | Variable |
|---|---|
| Application (client) ID | `client_id` |
| Directory (tenant) ID | `tenant_id` |

## 3. Create a Client Secret

1. In the left menu, click **Certificates & secrets**
2. Under **Client secrets**, click **+ New client secret**
3. Add a description (e.g. `OneDrive Access`) and choose an expiration
4. Click **Add**
5. **Immediately copy the generated secret value** — this is your `client_secret` and won't be shown again

## 4. Configure API Permissions

1. In the left menu, click **API permissions**
2. Click **Add a permission → Microsoft Graph → Delegated permissions**
3. Search for and select each of the following:
   - `Files.Read`
   - `Files.Read.All`
   - `Files.ReadWrite`
   - `Files.ReadWrite.All`
   - `User.Read`
4. Click **Add permissions**
5. Click **Grant admin consent**

---

> **Note:** The most critical step is selecting the correct **Supported account types** in Step 1 — it must include personal Microsoft accounts, as omitting this is the most common source of authentication errors.