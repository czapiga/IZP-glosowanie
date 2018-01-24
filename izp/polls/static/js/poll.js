
(function($) {
    function filter_answers(select) {
        $.ajax({
            type: 'GET',
            url: '/getanswers',
            data: {'selected': 'lol'},
            success: function(data) {
                console.log(data);
            },
            error: function(xhr){
                alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            }
        });
    }
    
    $(document).ready(function() {
       $('select[id$="depends_on"]').change(function () {
           filter_answers(this);
       });
    });

})(django.jQuery);