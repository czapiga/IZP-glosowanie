
(function($) {
    
    function filter_answers(select) {
        alert(select.id);
    }
    
    $(document).ready(function() {
       var element = document.getElementById('id_simplequestion_set-0-depends_on');
       $('select[id$="depends_on"]').change(function () {
           filter_answers(this);
       });
    });

})(django.jQuery);