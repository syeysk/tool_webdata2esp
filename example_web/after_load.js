document.getElementById('managing_btn_turn').addEventListener('click', function(e) {
    var input = e.target;
    sendform(input, 'turn', {data:{
        turn:input.dataset.value=='0'?'1':'0',
    },func_success: function(res, input) {
        input.dataset.value=input.dataset.value=='0'?'1':'0';
    }, arg_func_success:input});
});

document.getElementById('managing_btn_demo').addEventListener('click', function(e) {
    var input = e.target;
    sendform(input, 'demo', {data:{
        turn:input.dataset.value=='0'?'1':'0',
    },func_success: function(res, input) {
        input.dataset.value=input.dataset.value=='0'?'1':'0';
    }, arg_func_success:input});
});


//document.getElementById('managing_btn_color').addEventListener('change', ev_set_color);
document.getElementById('managing_btn_demo_speed').addEventListener('change', ev_set_demo_speed);

var cs = new ContentShower({
    navpanel: document.querySelector('.navpanel'),
    content_prefix: 'content_',
    content_active: 'managing',
    func_after_show: update_data
});

update_data('all', true);