(function($) {
    function filter_questions(select) {
        var index = select.id.toString().replace( /^\D+|\D+$/g, '');
        $.ajax({
            type: 'GET',
            url: '/getquestions',
            data: {'poll_name': $("#id_poll_name").val(), 'question_name': $("#id_simplequestion_set-" + index + "-question_text").val()},
            success: function(data) {
                for(i = 0; i < data.length; i++) {
                    $(select).append($('<option>', { value : i })
                             .text(data[i].question_text));  
                }
            },
        });
    }
    
    function filter_winner_choices(selected_question, choices_select) {
        $.ajax({
            type: 'GET',
            url: '/getchoices',
            data: {'question_name': selected_question},
            success: function(data) {  
                for(i = 0; i < data.length; i++) {
                    choices_select.append($('<option>', { value : i })
                             .text(data[i].choice_text));  
                }
            },
        });   
    }
    
    $(document).ready(function() {
       $('select[id$="depends_on"]').change(function () {
           var index = this.id.toString().replace( /^\D+|\D+$/g, '');
           $('#id_simplequestion_set-' + index + '-winner_choice').empty()
                           .append($('<option>', { value : '' })
                           .text('').attr('selected', true)); 
           filter_winner_choices(
               $(this).text(),
               $('#id_simplequestion_set-' + index + '-winner_choice')
           );
       });
    });
    
    $(window).load(function() {
        $('select[id$="depends_on"]').each(function() {
            $(this).empty(); 
            filter_questions(this);
            $(this).append($('<option>', { value : '' })
                           .text('').attr('selected', true)); 
        });
        
        $('select[id$="winner_choice"]').each(function() {
            $(this).empty();
            $(this).append($('<option>', { value : '' })
                           .text('').attr('selected', true)); 
        });
    });
    
})(django.jQuery);
