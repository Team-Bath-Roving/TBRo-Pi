import subprocess

# Cam can be passed as command line argument 

def getCamSettings(cam):
  out = subprocess.Popen(['v4l2-ctl', '-d', cam, '--list-ctrls-menu'],
             stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT)
  stdout,stderr = out.communicate()
  
  out = stdout.decode('UTF-8').splitlines()
  # print(out)
  camSettings = dict()

  nLines = len(out)
  # print(nLines)
  if nLines>1:
    for i in range(0, nLines):
      #Skip menu legend lines which are denoted by 4 tabs
      if out[i].startswith('\t\t\t\t'):
        continue

      a = dict()
      key_val = out[i].split(':',1)
      if len(key_val) > 1:
        setting = key_val[0].split()   
                # ['brightness', '0x00980900', '(int)']
        param = key_val[1].split()     
                # ['min=-64', 'max=64', 'step=1', 'default=0', 'value=0']
        # Put paramaters into a dictionary
        for j in range(0, len(param)):
          param_pair=param[j].split('=',1)
          # print(param_pair)
          param_dict={}
          if len(param_pair)>1:
            a[param_pair[0]]=param_pair[1]
          else:
            a[param_pair[0]]=None
        # Add bitName and setting type to params dictionary 
        a.update({'bitName': setting[1]})
        a.update({'type': setting[2].strip("()")})
        # Create a legend for menu entries and add to dictionary with other params
        # if a['type'] == 'menu':
        #   h = 0
        #   legend = ''
        #   while h >= 0:
        #     h += 1
        #     ih = i + h
        #     if out[ih].startswith('\t\t\t\t') and (ih) <= nLines:
        #       legend = legend + out[i+h].strip() + "   "
        #     else:
        #       h = -1
        #   a.update({'legend': legend})    # additional data on settings
        #   a.update({'step': 1})           # adding to work with updateUVCsetting()
        # Use setting name as key and dictionary of params as value
        camSettings.update({setting[0]: a})
  else:
    camSettings={}
  # for x in camSettings:
  #   print(x,'\n   ',camSettings[x])
  
  return camSettings

def updateUVCsetting(cam, setting, value):
                  # ('gamma', 1   , 30 )
  #v4l2-ctl -d /dev/video0 --set-ctrl=brightness=50
  subprocess.call(['v4l2-ctl', '-d', cam, 
      f'--set-ctrl={setting}={value}'], shell=False)
  # check = subprocess.check_output(['v4l2-ctl', '-d', cam, 
  #     f'--get-ctrl={setting}'], shell=False).decode('UTF-8').lstrip().split()[1]
  # test = "passed" if int(value) == int(check) else "fail"
  # print(f'setting requested -- {setting} -->  {value}    test: {test}')