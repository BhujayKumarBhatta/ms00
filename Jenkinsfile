node() 
{
    stage 'Checkout'
    checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'acaa3a6e-795b-4869-9845-9fdae5a7d440', url: 'https://gitlab.net.itc/tsp-billing/tokenleader.git']]])
	gitlabCommitStatus 
	{
             stage('remove-remote-repo') 
                 {
                 
                 
                     echo 'Removing repo from reomte server'
                     sh "ssh tokenleader 'sudo rm -rf /home/jenkins/tokenleader-pipe'"
                     
                 
                 }
                 stage('Copy-Repo-from-jenkins') 
                 {
                  
                 
                     echo 'Copy repo from jenkins server to remote machine'
                     sh "scp -r /var/lib/jenkins/workspace/tokenleader-pipe jenkins@tokenleader:/home/jenkins"
                     sh "ssh tokenleader 'chmod +x /home/jenkins/tokenleader-pipe/jenkins.sh'"
                                
                 
                 }
            	
            	stage('Build-Test') 
            	{
                 
                     echo 'dos2unix conversion of shell'
                     sh "ssh tokenleader 'dos2unix /home/jenkins/tokenleader-pipe/jenkins.sh'"
                     echo 'Build the virtual environment and test the code'
                     sh "ssh  tokenleader '/home/jenkins/tokenleader-pipe/jenkins.sh'"
                     
                 
            	}
        
    }
}
