$(document).ready(function() {
    $('#local').prop('checked',true);
    $("input[type='radio']").click(function(){
        // ftp_cred
        $(".stream-path,.ftp-submit").css("display","inline-block");
        $("#stream-form *").prop('disabled', true);
        let val = $("input[name='stream_type']:checked").val();
        if(val == "ftp"){
            $(".ftp_cred").css("display","inline-block");
            $("#upload-quote").html("FTP Path:");
            $("#upload_stream_path").attr("placeholder", "Enter Path");
            $(".tsduck_sub_command").hide();
            $(".cmd_selection").hide();
            $(".head_sub_cmd").hide();
        }
        else if(val == "http"){
            $(".ftp_cred").css("display","none");
            $("#upload-quote").html("Stream URL:");
            $("#upload_stream_path").attr("placeholder", "Enter URL");
            $('#host_ip').attr('required', false);
            $('#username').attr('required', false);
            $('#password').attr('required', false);
            $(".tsduck_sub_command").hide();
            $(".cmd_selection").hide();
            $(".head_sub_cmd").hide();
        }
        else if(val == "local"){
            $(".ftp_cred").css("display","none");
            $('#local').prop('checked',true);
            $("#stream-form *").prop('disabled', false);
            $(".stream-path,.ftp-submit").css("display","none");
        }
    });
});

function ajaxSuccessOutput(data){
    $("#upload-icon").css('display','none');
    setTimeout( 
        function(){
            alert(data.message);
            if(data.percentage == "100"){
                location.reload();
            }
        }, 100);
}
function ajaxErrorOutput(data){
    $("#upload-icon").css('display','none');
    setTimeout(
        function(){
            alert(data.responseJSON.error);
        }, 100);
}

$(document).ready(function(){
    $("#submit_upload").click(function(e){
        var valid = this.form.checkValidity();
        if(valid){
            event.preventDefault(); // Stops normal form submission so that we can submit using ajax
            let stream_type = $("input[name='stream_type']:checked").val();
            let host_ip = document.getElementById("host_ip");
            let username = document.getElementById("username");
            let password = document.getElementById("password");
            let stream_path = document.getElementById("stream_path");
            let csrf_upload = $('#ftp-stream').find('input[name=csrfmiddlewaretoken]').val();
            $("#upload-icon").css('display','inline-block');
            $.ajax({
                type: "POST",
                url: '/tsduck/analyze/upload',
                data: {
                        'csrfmiddlewaretoken' : csrf_upload,
                        'stream_type': stream_type,
                        'host_ip' : host_ip.value,
                        'username': username.value,
                        'password': password.value,
                        'stream_path': stream_path.value
                    },
                dataType: "JSON",
                ContentType : 'application/x-www-form-urlencoded',
                success : function(data){
                    ajaxSuccessOutput(data);
                },
                error : function(data){
                    ajaxErrorOutput(data);
                }
            });
        }
    });
});

function ajaxSuccessOutputForDelete(data){
    $("#delete-icon").css('display','none');
    setTimeout( 
        function(){
            alert(data.message);
            location.reload();
        }, 100);
}
function ajaxErrorOutputForDelete(data){
    $("#delete-icon").css('display','none');
    setTimeout(
        function(){
            alert("Error: Json response!");
        }, 100);
}
$(document).ready(function() {
    $("#delete_stream").click(function(e){
        event.preventDefault(); // Stops normal form submission so that we can submit using ajax
        let stream_type = $("input[name='stream_type']:checked").val();
        let selected_streams = [];
        $(".each_streams").each(function(){
           if($(this).prop("checked") == true){
                selected_streams.push($(this).val());
           }
        });
        if(selected_streams.length == 0){
            alert("Please select atleast one Stream!");
            return;
        }
        $("#delete-icon").css('display','inline-block');
        let host_ip = document.getElementById("host_ip");
        let csrf_delete = $('#delete_form').find('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            type: "POST",
            url: '/tsduck/analyze/delete-streams',
            data: {
                    'csrfmiddlewaretoken' : csrf_delete,
                    'selected_streams': selected_streams,
                },
            dataType: "JSON",
            ContentType : 'application/x-www-form-urlencoded',
            success : function(data){
                ajaxSuccessOutputForDelete(data);
            },
            error : function(data){
                ajaxErrorOutputForDelete(data);
            }
        });
    });
});

function ajaxSuccessOutputForAnalysis(data){
    $("#analyze-icon").css('display','none');
    setTimeout(
        function(){
            alert("Successful");
            $(".cmd-output").css("display","inline-block");
            document.getElementById("tsduck_cmd").innerHTML = "";
            document.getElementById("save_output").innerHTML = "";
            $("#tsduck_cmd").append(data.tsduck_command);
            $("#save_output").append(data.cmd_result);
        }, 100);
}
function ajaxErrorOutputForAnalysis(data){
    $("#analyze-icon").css('display','none');
    setTimeout(
        function(){
            alert("Error: Json response!");
        }, 100);
}
$(document).ready(function() {
    $("#submit").click(function(e){
        event.preventDefault(); // Stops normal form submission so that we can submit using ajax
        let stream_name = $("#stream_name").val();
        let tsduck_command = $("#tsduck_main_command").val();
        let full_command = $("#full_command").val();
        let tsduck_sub_commands = [];
        $("input[name='tsduck_sub_command']").each(function(){
           if($(this).prop("checked") == true){
                tsduck_sub_commands.push($(this).val());
           }
        });
        let csrf_analyze = $('#stream-form').find('input[name=csrfmiddlewaretoken]').val();
        $("#analyze-icon").css('display','inline-block');
        if(tsduck_command !== "tstables"){
            $.ajax({
                type: "POST",
                url: '/tsduck/analyze/result',
                data: {
                        'csrfmiddlewaretoken' : csrf_analyze,
                        'stream_name': stream_name,
                        'tsduck_command' : tsduck_command,
                        'tsduck_sub_commands' : tsduck_sub_commands,
                        'full_command' : full_command
                    },
                dataType: "JSON",
                ContentType : 'application/x-www-form-urlencoded',
                success : function(data){
                    ajaxSuccessOutputForAnalysis(data);
                },
                error : function(data){
                    ajaxErrorOutputForAnalysis(data);
                }
            });
        }
        else{
            let pid_value = $("#pid_value").val();
            let tid_value = $("#tid_value").val();
            $.ajax({
                type: "POST",
                url: '/tsduck/analyze/tstables-result',
                data: {
                        'csrfmiddlewaretoken' : csrf_analyze,
                        'stream_name': stream_name,
                        'tsduck_command' : tsduck_command,
                        'tsduck_sub_commands' : tsduck_sub_commands,
                        'pid_value' : pid_value,
                        'tid_value' : tid_value
                    },
                dataType: "JSON",
                ContentType : 'application/x-www-form-urlencoded',
                success : function(data){
                    ajaxSuccessOutputForAnalysis(data);
                },
                error : function(data){
                    ajaxErrorOutputForAnalysis(data);
                }
            });
        }
    });
});

$("#avail_streams").on('click', function(){
    $("#all_streams").css("display", "inline-block");
});

$("#select_stream").on('click', function() {
    if($("#delete_stream").css("display") === "none"){
        $("#delete_stream").css("display", "inline-block");
        $("input[name='each_streams']").css("display", "inline-block");
    }
    else{
        $("#delete_stream").css("display", "none");
        $("input[name='each_streams']").css("display", "none");
    }
});

$("#close_popup").on('click', function(){
    $("#all_streams").css("display", "none");
    $("#delete_stream").css("display", "none");
    $("input[name='each_streams']").css("display", "none");
});

$(document).mouseup(function (e) {
    if ($(e.target).closest(".tsduck_command").length === 0) {
        $(".items").hide();
    }
});
$(".anchor").click(function() {
    let a = $(this).next(".items");
    if(a.css("display") === "block"){
        $(this).css("color","#0094ff");
        a.hide();
    }
    else{
        $(this).css("color","#444444");
        $(".items").hide();
        a.show();
    }
});
$("#tscommand").change(function(){
    $(".tsduck_sub_command").hide();
    $("#direct_input").hide();
    $("#generic_option").show();
    $('input[type=checkbox]').prop('checked',false);
    let checked_items = document.getElementsByClassName("checked_items");
    for(let i=0;i<checked_items.length;i++){
        checked_items[i].innerHTML = "";
    }
    $(".cmd_selection").show();
    $(".head_sub_cmd").show();
    $("#streamPath").show();
    if($("#tscommand option:selected").attr('id') === 'tsanalyze'){
        $(".tsanalyze_option").show();
    }
    else if($("#tscommand option:selected").attr('id') === 'tspsi'){ 
        $(".tspsi_option").show();
    }
    else if($("#tscommand option:selected").attr('id') === 'tsdump'){ 
        $(".tsdump_option").show();
    }
    else if($("#tscommand option:selected").attr('id') === 'tsscan'){ 
        $(".tsscan_option").show();
        $("#streamPath").hide();
    }
    else if($("#tscommand option:selected").attr('id') === 'select'){ 
        $("#generic_option").hide();
        $(".cmd_selection").hide();
        $(".head_sub_cmd").hide();
    }
    else if($("#tscommand option:selected").attr('id') === 'custom'){ 
        $("#direct_input").show();
        $("#generic_option").hide();
        $(".head_sub_cmd").hide();
    }
    else if($("#tscommand option:selected").attr('id') === 'tstables'){ 
        $(".tstables_option").show();
    }
});

$('#tstables_option1').on('change', function() {
    let tstables_input = $("#tstables_option1 :input");
    for(let i=0;i<tstables_input.length;i++){
        let input_value = tstables_input[i].value;
        if(input_value === "-p"){
            if(tstables_input[i].checked){
                $("#pid_table").css('display','inline-block');
            }
            else{
                $("#pid_table").hide();
            }
        }
        if(input_value === "-t"){
            if(tstables_input[i].checked){
                $("#tid_table").css('display','inline-block');
            }
            else{
                $("#tid_table").hide();
            }
        }
    }
});

$('input[name="tsduck_sub_command"]').on('change', function() {
    let val = this.value;
    let flag = this.checked ? true : false;
    let item = $(this).parents()[3];
    let x = document.getElementById(item.id);
    let y = x.getElementsByTagName("span")[0];
    if(flag){
        y.append(" "+val);  
    }
    else{
        let all_items = y.innerHTML.split(" ");
        let i = 0
        let new_items = "";
        for(i=0;i<all_items.length;i++){
            if(!(all_items[i] === val)){
                new_items += " " + all_items[i];
            }
        }
        y.innerHTML = "";
        y.append(new_items);
    }
});
function download(file, text) {             
    //creating an invisible element
    var element = document.createElement('a');
    element.setAttribute('href', 
    'data:text/plain;charset=utf-8, '
    + encodeURIComponent(text));
    element.setAttribute('download', file);
    // Above code is equivalent to
    // <a href="path of file" download="file name"> 
    document.body.appendChild(element);
    //onClick property
    element.click();
    document.body.removeChild(element);
}
function commandOutputData(){
    let htmlText = document.getElementById("save_output");
    if(htmlText != null){
        let text = htmlText.innerHTML;
        text = text.replaceAll("&#39;","'");
        text = text.replaceAll("&#x27;","'");
        text = text.replaceAll("&amp;","&");
        text = text.replaceAll("&quot;",'"');
        text = text.replaceAll("&lt;","<");
        text = text.replaceAll("&gt;",">");
        htmlText.innerHTML = "";
        htmlText.append(text);
    }
}
commandOutputData();
function saveOutputData() {
    let htmlText = document.getElementById("save_output");
    let cmd_output = htmlText.innerHTML;
    let x = cmd_output.split("<br>");
    let text = "";
    for(let i=0;i<x.length;i++){
        if(x[i].replace(/\s/g, '').length){
            text = text + x[i].trimStart();
        }
    }
    text = text.replaceAll("&#39;","'");
    text = text.replaceAll("&#x27;","'");
    text = text.replaceAll("&amp;","&");
    text = text.replaceAll("&quot;",'"');
    text = text.replaceAll("&lt;","<");
    text = text.replaceAll("&gt;",">");
    let filename = "tsduck.txt";
    download(filename, text);
}
