https://docs.google.com/document/d/1OxlWEItvGYA3h5Xw2SVTNDlPV1f830fRT1CJ_a6mtxI/edit?tab=t.0
Started by upstream project "pipeline" build number 
1
originally caused by:
 Started by user 
admin
Running as SYSTEM
Building in workspace /var/lib/jenkins/workspace/Download
The recommended git tool is: NONE
using credential 879771bd-48bc-49c2-aa20-16dc7aadac4e
Cloning the remote Git repository
Cloning repository git@github.com:kirilman/MLops.git
 > git init /var/lib/jenkins/workspace/Download # timeout=10
Fetching upstream changes from git@github.com:kirilman/MLops.git
 > git --version # timeout=10
 > git --version # 'git version 2.34.1'
using GIT_SSH to set credentials 
Verifying host key using known hosts file
 > git fetch --tags --force --progress -- git@github.com:kirilman/MLops.git +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git config remote.origin.url git@github.com:kirilman/MLops.git # timeout=10
 > git config --add remote.origin.fetch +refs/heads/*:refs/remotes/origin/* # timeout=10
Avoid second fetch
 > git rev-parse refs/remotes/origin/main^{commit} # timeout=10
Checking out Revision 5e493af22bc7c956d96da83c9270120c6280ede4 (refs/remotes/origin/main)
 > git config core.sparsecheckout # timeout=10
 > git checkout -f 5e493af22bc7c956d96da83c9270120c6280ede4 # timeout=10
Commit message: "add mlflow serve"
First time build. Skipping changelog.
[Download] $ /bin/sh -xe /tmp/jenkins3112968798170198204.sh
+ python3 -m venv ./my_env
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.10-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /var/lib/jenkins/workspace/Download/my_env/bin/python3

Build step 'Выполнить команду shell' marked build as failure
Finished: FAILURE
