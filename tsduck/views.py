from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
import paramiko, json, time, io

# TSDuck credentials
host = "10.221.52.72"
port = 22
tsUser = "tsduck"
tsPass = "tsduck"

user_list = ['amresh.verma','santhosh.srinivasan','pg.sundaram','poovalingam.m','shashikumar06.n','sasikumar.j','satheesh.r','nagamanickam.v','prasad14.kothawade','keerthee.rajang','bhushan.jadhav','pooja.pandey','harshada.dhopte','vinayaraj28.nayak','vijetha.s']

def ts_index(request):
	if request.user.is_authenticated:
		print("User Authenticated!")
		return redirect("/tsduck/analyze")
	else:
		print("User not signed in!")
		return render(request,"tsindex.html")

def authenticate(request):
	global host, port, tsUser, tsPass
	if request.user.is_authenticated:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, port, tsUser, tsPass)
		time.sleep(3)
		stdout = ""
		command = "cd temp; ls"
		stdin, stdout, stderr = ssh.exec_command(command)
		only_stream = []
		all_streams = []
		for strm in stdout.readlines():
			if((len(strm.split(".ts")) == 2) or (len(strm.split(".mpg")) == 2) or (len(strm.split(".ps")) == 2) or (len(strm.split(".3gp")) == 2) or (len(strm.split(".3gpp")) == 2)):
				only_stream.append(strm)
			all_streams.append(strm)
		ssh.close()
		return render(request,"tsduck.html",{"all_streams":all_streams,"only_stream":only_stream})
	elif request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]
		if User.objects.filter(username=username).exists():
			user = auth.authenticate(username=username,password=password)
			if user is not None:
				auth.login(request,user)
				# Do SSH Connection and use commands
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(host, port, tsUser, tsPass)
				time.sleep(3)
				command = "cd temp; ls"
				stdin, stdout, stderr = ssh.exec_command(command)
				only_stream = []
				all_streams = []
				for strm in stdout.readlines():
					if((len(strm.split(".ts")) == 2) or (len(strm.split(".mpg")) == 2) or (len(strm.split(".ps")) == 2) or (len(strm.split(".3gp")) == 2) or (len(strm.split(".3gpp")) == 2)):
						only_stream.append(strm)
					all_streams.append(strm)
				ssh.close()
				return render(request,"tsduck.html",{"all_streams":all_streams,"only_stream":only_stream})
			else:
				messages.info(request, "Incorrect Password!")
			return redirect("/tsduck")
		else:
			if username in user_list:
				user1 = User.objects.create_user(username=username,password=password)
				user1.save()
				user = auth.authenticate(username=username,password=password)
				if user is not None:
					auth.login(request,user)
					# Do SSH Connection and use commands
					ssh = paramiko.SSHClient()
					ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh.connect(host, port, tsUser, tsPass)
					time.sleep(3)
					command = "cd temp; ls"
					stdin, stdout, stderr = ssh.exec_command(command)
					only_stream = []
					all_streams = []
					for strm in stdout.readlines():
						if((len(strm.split(".ts")) == 2) or (len(strm.split(".mpg")) == 2) or (len(strm.split(".ps")) == 2) or (len(strm.split(".3gp")) == 2) or (len(strm.split(".3gpp")) == 2)):
							only_stream.append(strm)
						all_streams.append(strm)
					ssh.close()
					return render(request,"tsduck.html",{"all_streams":all_streams,"only_stream":only_stream})
				else:
					messages.info(request, "Authentication Failed!")
			else:
				messages.info(request, "You don't have permission to login. Please contact to Admin for permission.")
			return redirect("/tsduck")
	return redirect("/tsduck")

@login_required(login_url='/tsduck')
def cmd_result(request):
	if request.method == "POST":
		global host, port, tsUser, tsPass
		sub_command = ""
		tsduck_command = ""
		stream_name = request.POST.get("stream_name")
		repo_path = "lgsitsduck/tsduck/tsduck-master"
		tsduck_command = request.POST.get("tsduck_command")
		sub_command = request.POST.getlist("tsduck_sub_commands[]")
		stream_path = "/home/tsduck/temp/" + stream_name.strip()
		print("stream_name=",stream_name,"tsduck_command=",tsduck_command)
		print("sub-commands=",sub_command)
		if tsduck_command == "custom":
			tsduck_command = request.POST.get("full_command")
		if tsduck_command == "tsscan":
			stream_path = ""
		str_sub_command = ""
		for each in sub_command:
			str_sub_command = str_sub_command + each + " "
		if str_sub_command == "":
			tsduck_command = tsduck_command + " " + stream_path
		else:
			tsduck_command = tsduck_command + " " + str_sub_command + stream_path
		command = "cd " + repo_path + "; source build/setenv.sh; " + tsduck_command
		stdout = ""
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, port, tsUser, tsPass)
		time.sleep(1)
		chan = ssh.get_transport().open_session()
		chan.settimeout(300)
		chan.exec_command(command)
		contents = io.StringIO()
		error = io.StringIO()
		while not chan.exit_status_ready():
			if chan.recv_ready():
				data = str(chan.recv(1024).decode("utf-8"))
				print("Inside stdout")
				while data.strip():
					contents.write(data)
					data = str(chan.recv(1024).decode("utf-8"))
			if chan.recv_stderr_ready():
				error_buff = str(chan.recv_stderr(1024).decode("utf-8"))
				print("Inside stderr")
				while error_buff:
					error.write(error_buff)
					error_buff = str(chan.recv_stderr(1024).decode("utf-8"))
		exit_status = chan.recv_exit_status()
		output_value = contents.getvalue()
		error_value = error.getvalue()
		if len(output_value) == 0:
			output_value = error_value
			error_value = []
		if len(error_value)==0:
		    print("Output Data Stored!")
		else:
		    print("There was no output for this command")
		output = ""
		avail_stream = "cd temp; ls"
		stdin, output, stderr1 = ssh.exec_command(avail_stream)
		only_stream = []
		all_streams = []
		for strm in output.readlines():
			if((len(strm.split(".ts")) == 2) or (len(strm.split(".mpg")) == 2) or (len(strm.split(".ps")) == 2) or (len(strm.split(".3gp")) == 2) or (len(strm.split(".3gpp")) == 2)):
				only_stream.append(strm)
			all_streams.append(strm)
		ssh.close()
		return JsonResponse({"tsduck_command":tsduck_command, "cmd_result":output_value, "all_streams":all_streams,"only_stream":only_stream})
	return redirect("/tsduck/analyze")

@login_required(login_url='/tsduck')
def stream_edit(request):
	if request.method == "POST":
		global host, port, tsUser, tsPass
		sub_command = ""
		tsduck_command = ""
		stream_name = request.POST.get("stream_name")
		pid_value = request.POST.get("pid_value")
		tid_value = request.POST.get("tid_value")
		repo_path = "lgsitsduck/tsduck/tsduck-master"
		tsduck_command = request.POST.get("tsduck_command")
		sub_command = request.POST.getlist("tsduck_sub_commands[]")
		stream_path = "/home/tsduck/temp/" + stream_name.strip()
		print("stream_name=",stream_name,"tsduck_command=",tsduck_command)
		print("sub-commands=",sub_command)
		str_sub_command = ""
		for each in sub_command:
			if(each == "-p"):
				each = each + " " + str(pid_value)
			elif(each == "-t"):
				each = each + " " + str(tid_value)
			str_sub_command = str_sub_command + each + " "
		if str_sub_command == "":
			tsduck_command = tsduck_command + " " + stream_path
		else:
			tsduck_command = tsduck_command + " " + str_sub_command + stream_path
		command = "cd " + repo_path + "; source build/setenv.sh; " + tsduck_command
		print(tsduck_command)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, port, tsUser, tsPass)
		time.sleep(1)
		chan = ssh.get_transport().open_session()
		chan.settimeout(300)
		chan.exec_command(command)
		contents = io.StringIO()
		error = io.StringIO()
		while not chan.exit_status_ready():
			if chan.recv_ready():
				data = str(chan.recv(1024).decode("utf-8"))
				print("Inside stdout")
				while data.strip():
					contents.write(data)
					data = str(chan.recv(1024).decode("utf-8"))
			if chan.recv_stderr_ready():
				error_buff = str(chan.recv_stderr(1024).decode("utf-8"))
				print("Inside stderr")
				while error_buff:
					error.write(error_buff)
					error_buff = str(chan.recv_stderr(1024).decode("utf-8"))
		exit_status = chan.recv_exit_status()
		output_value = contents.getvalue()
		error_value = error.getvalue()
		if len(output_value) == 0:
			output_value = error_value
			error_value = []
		if len(error_value)==0:
		    print("Output Data Stored!")
		else:
		    print("There was no output for this command")
		ssh.close()
		return JsonResponse({"tsduck_command":tsduck_command, "cmd_result":output_value})
	return redirect("/tsduck")

@login_required(login_url='/tsduck')
def delete_stream(request):
	if request.method == "POST":
		global host, port, tsUser, tsPass
		streams = request.POST.getlist("selected_streams[]")
		command = "cd temp; rm -rf "
		lscmd = "cd temp; ls"
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, port, tsUser, tsPass)
		time.sleep(3)
		for strm1 in streams:
			strm = strm1.strip()
			stdin_ls, stdout_ls, stderr_ls = ssh.exec_command(lscmd)
			flag = 0
			for each_strm in stdout_ls.readlines():
				each_strm = each_strm.strip()
				if(each_strm == strm):
					print("File matched!")
					flag = 1
					dltcmd = command + strm
					stdin, stdout, stderr = ssh.exec_command(dltcmd)
					time.sleep(1)
			if(flag == 0):
				return JsonResponse({'message': 'File does not exist!','filename':strm})
		ssh.close()
		return JsonResponse({'message': 'Files deleted Successfully!'})
	return redirect("/tsduck")

@login_required(login_url='/tsduck')
def upload_stream(request):
	if request.method == "POST":
		global host, port, tsUser, tsPass
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, port, tsUser, tsPass)
		time.sleep(3)
		stream_type = request.POST.get("stream_type", None)
		command = ""
		if(stream_type == "ftp"):
			host_ip = request.POST.get("host_ip", None)
			username = request.POST.get("username", None)
			password = request.POST.get("password", None)
			stream_path = request.POST.get("stream_path", None)
			split_path = stream_path.split("/")
			stream_flag = split_path[len(split_path)-1]
			stream_name = "1";
			command = "sftp " + username + "@" + host_ip + ":" + stream_path + " temp/"
			stdin, stdout, stderr = ssh.exec_command('cd temp; ls')
			stream_info = stdout.readlines()
			for stm in stream_info:
				if(stm.split("\n")[0] == stream_flag):
					ssh.close()
					return JsonResponse({'message': 'File is already available!'})
			# ============Channel Open=======================
			channel = ssh.invoke_shell()
			channel_data = str()
			i = 0
			while(i<6):
				print("\n==================================Inside While Loop==================================\n")
				i += 1
				channel_data = str(channel.recv(9999).decode("utf-8"))
				print("\n==================================channel Data==================================\n")
				print(channel_data)
				print("\n========================================END========================================\n")
				if "Connection closed" in channel_data:
					ssh.close()
					return JsonResponse({"message": "Wrong IP Address!"})
				elif "tsduck@dvbs-s1:~$" in channel_data or "swfarm-siuo04:~$" in channel_data:
					print("\n==================================execute command==================================\n")
					channel.send(command)
					channel.send('\n')
				elif "yes/no" in channel_data:
					print("\n==================================yes/no==================================\n")
					channel.send('yes')
					channel.send('\n')
				elif "password:" in channel_data:
					print("\n==================================Enter password==================================\n")
					channel.send(password)
					channel.send('\n')
					time.sleep(2)
					i = 5
					while(True):
						if(channel.recv_ready()):
							channel_data = str(channel.recv(9999).decode("utf-8"))
							time.sleep(2)
							print("\n==================================channel Data==================================\n")
							print(channel_data)
							print("\n========================================END========================================\n")
							i = 6
							if "not found" in channel_data:
								ssh.close()
								return JsonResponse({'message': 'Incorrect File Path!'})
							if "100%" in channel_data:
								ssh.close()
								return JsonResponse({'message': 'File Upload Successful!','stream_name':stream_flag, 'percentage' : "100"})
							if "Permission denied" in channel_data:
								ssh.close()
								return JsonResponse({'message': 'Incorrect Username or Password!'})
				time.sleep(2)
			channel.close()
			# ============Channel Closed=====================
		elif(stream_type == "http"):
			url_path = request.POST["stream_path"]
			url_list = url_path.split("/")
			stream_flag = url_list[len(url_list)-1]
			upload_status = "File Upload Failed!"
			command = "wget " + url_path + " temp/"
			stdin, stdout, stderr = ssh.exec_command(command)
			time.sleep(5)
			if "100%" in stderr.readlines() or len(stderr.readlines()) == 0:
				upload_status = stream_flag
			print("stderr=",stderr.readlines())
			print("stdout=",stdout.readlines())
			ssh.close()
			return JsonResponse({'message': 'File Upload Successful!', 'stream_name': upload_status})
		ssh.close()
		return JsonResponse({'message': 'Success'})
	return redirect("/tsduck")

@login_required(login_url='/tsduck')
def session_close(request):
	if request.method == "POST":
		auth.logout(request)
		messages.info(request, 'Logged Out Successfully!')
	return redirect("/tsduck")