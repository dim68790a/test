Started by upstream project "pipeline" build number 
6
originally caused by:
 Started by user 
admin
Running as SYSTEM
Building in workspace /var/lib/jenkins/workspace/train
[train] $ /bin/sh -xe /tmp/jenkins15208351925060392934.sh
+ echo Start train model
Start train model
+ cd /var/lib/jenkins/workspace/Download/
+ . ./my_env/bin/activate
+ deactivate nondestructive
+ [ -n  ]
+ [ -n  ]
+ [ -n  -o -n  ]
+ [ -n  ]
+ unset VIRTUAL_ENV
+ unset VIRTUAL_ENV_PROMPT
+ [ ! nondestructive = nondestructive ]
+ VIRTUAL_ENV=/var/lib/jenkins/workspace/Download/my_env
+ export VIRTUAL_ENV
+ _OLD_VIRTUAL_PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
+ PATH=/var/lib/jenkins/workspace/Download/my_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
+ export PATH
+ [ -n  ]
+ [ -z  ]
+ _OLD_VIRTUAL_PS1=$ 
+ PS1=(my_env) $ 
+ export PS1
+ VIRTUAL_ENV_PROMPT=(my_env) 
+ export VIRTUAL_ENV_PROMPT
+ [ -n  -o -n  ]
+ python3 train_model.py
2026/04/20 14:41:28 INFO mlflow.tracking.fluent: Experiment with name 'California Housing Linear Models' does not exist. Creating a new experiment.
