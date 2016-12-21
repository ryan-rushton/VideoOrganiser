/**
 * Created by ryanrushton on 11/12/16.
 */


function show_video(video_path) {
    var string = video_path
    $('#file_system_jumbo').text(string)
    $('#file_system_jumbo').append('<video width="320" height="240" controls>' +
        '<source src=""'+ string +'" type="video/mp4"> Your browser does not support the video tag. </video>')
}

function play_in_vlc(video_path) {
    $.getJSON("{% url play_vlc %}?video_path="+video_path)
}

function get_file_system(current_dir){
    current_dir = "?new_dir="+current_dir || "";
    $.getJSON("http://localhost:8000/ajax/load_file_system/"+current_dir,
        function (data) {
            $('#file_system_jumbo').text("")
            $('#file_system_list').text("")
            var top_line = '<p><span class="glyphicon glyphicon-folder-open"></span>'+ data.current_dir +'</p>';
            $('#file_system_jumbo').append(top_line).append('<ul class="list-group" id="file_system_list"></ul>');
            $.each(data.child_dirs, function(index, value){
                $('#file_system_list').append('<li class="list-group-item"><p><a ' +
                    'onclick="get_file_system(\''+value[1]+'\');">' +
                    '<span class="glyphicon glyphicon-folder-close"></span> '+value[0]+'</a></p></li>')
            });
            $.each(data.child_files, function(index, value){
                $('#file_system_list').append('<li class="list-group-item"><p>' +
                    '<span class="glyphicon glyphicon-file"></span>'+value[0]+'</p></li>')
            });
        }
    )
}

function get_genre_func(){
    $.ajax("http://localhost:8000/ajax/get_genre/",
        {success:function build_modal(data){
                if (data.contains_data == true){
                    var genre_form = data.genre_form;
                    var file_name = data.file_name;
                    var intro = 'Pick a genre for '+file_name
                    var end = genre_form + '<input type="submit" id="genreSubmit" style="margin-top: 10px" ' +
                        'class="btn btn-default" value="Confirm" onclick="setTimeout(get_genre_func, 2000)"/>'
                    $('#genreModalBodyTop').text("");
                    $('#genreModalBodyTop').append(intro);
                    $('#genreFormBody').text("");
                    $('#genreFormBody').append(end)

                    $('#genreModal').modal('show');
                }
                else{
                    setTimeout(get_genre_func, 3000)
                }

            }
        }
        )
}

$('#genreModal').modal()
