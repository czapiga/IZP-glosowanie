
(function($) {
    function filter_questions(select_id) {
        var index = select_id.replace( /^\D+|\D+$/g, '');
        $.ajax({
            type: 'GET',
            url: '/getquestions',
            data: {'poll_name': $("#id_poll_name").val(), 'question_name': $("#id_simplequestion_set-" + index + "-question_text").val()},
            success: function(data) {
                questions = [];
                for(i = 0; i < data.length; i++) {
                    questions.push(data[i].question_text);
                }
                console.log(questions);
                document.getElementById(select_id).options = questions;
            },
            error: function(xhr){
                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });
    }
    
    $(document).ready(function() {
       $('select[id$="depends_on"]').change(function () {
                   var index = this.id.toString().replace( /^\D+|\D+$/g, '');

           console.log(index);
           filter_questions(this.id.toString());
       });
    });
    $(window).load(function() {
                    $('select[id$="depends_on"]').each(function() {filter_questions(this.id.toString());});

    });
})(django.jQuery);

