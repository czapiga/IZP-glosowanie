(function($) {
    function filter_questions(select) {
        $.ajax({
            type: 'GET',
            url: '/getquestions',
            data: {'poll_name': $("#id_poll :selected").text(), 'question_name': $("#id_question_text").val()},
            success: function(data) {
                for(i = 0; i < data.length; i++) {
                    $(select).append($('<option>', { value : data[i].question_text })
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
                    choices_select.append($('<option>', { value : data[i].choice_text })
                             .text(data[i].choice_text));  
                }
            },
        });   
    }
    
    $(document).ready(function() {
       $('select[id$="depends_on"]').change(function () {
           var index = this.id.toString().replace( /^\D+|\D+$/g, '');
           $('#id_winner_choice').empty()
                           .append($('<option>', { value : '' })
                           .text('').attr('selected', true)); 
           filter_winner_choices(
               $(this).val(),
               $('#id_winner_choice')
           );
       });
        
      $('#id_poll').change(function() { 
          $('#id_depends_on').empty();
          filter_questions($('#id_depends_on'));
          $('#id_depends_on').append($('<option>', { value : '' })
                           .text('').attr('selected', true));
          $('#id_winner_choice').empty()
              .append($('<option>', { value : '' })
                           .text('').attr('selected', true)); 
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
