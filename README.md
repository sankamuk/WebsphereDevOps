# WebsphereDevOps

This tool will help you build your own Infrastructure As Code (IAC) solution for IBM Websphere Application Server.


## Usage

The whole framework is Property file based.
  1. The complete Infrastructure is managed and maintained using Property files which should be version managed and secured.
  2. WAS hosting infrastructure(PaaS) is designed to consist of one single Cell and individual applications deployed on it.
  3. The Cell Scoped configurations are managed and maintained with one configuration file which will be applied using was_85_dmgr.py.
  4. Applications are independent components maintained using its own property file which will be applied using was_85_admin.py.
  5. Thus your whole infrastucture will consist of one Cell configuration file and multiple Application configuration files.
  6. Any changes made to the corresponding infrasrtucture component should be made via chenging corresponding configuration file,
     then the configuration is pushed in actual environment by running corresponding script with the propert file.
     
NOTE: 
* Application configuration can be build from scratch by running the jython script with property file but Cell configurations should be used to manage the Cell. A basis Cell environment should be build manually and the corresponding Jython script canno build a WAS ND Cell cannot be build from scratch using the script.
* The tool is visioned to be used with a PaaS Cell build with WAS ND with Virtual Enterprise. But its not a mandate or requirement.

## Support and managebility

If you are reading this README file then you are probably about to use the my tools to administer IBM Websphere Application Server Good choice. This tool is made for you. Moreover this tool is free and always will be thats my promise.

Now it is hard to believe that you will get 24/7 Support thats too much to ask for. But in case you face any issue or need setup and usage guidance and want my intervention and you cannot debug the hundreeds lines of Jython code your self, please do not hassitate to write to me. Its a guarentee you will get an answer but it is not a guarentee you will have it in a SLA.

Reach Me: sanmuk21@gmail.com

Best of luck. 
