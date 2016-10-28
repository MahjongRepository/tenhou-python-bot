$(function () {
    $.get('/data/' + replay_id, function (data) {
        process_replay(data);
    });
});

function process_replay(tags) {
    tags.forEach(function (element) {

    })
}