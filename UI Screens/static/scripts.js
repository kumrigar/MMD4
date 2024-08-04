document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(message) {
            message.style.display = 'none';
        });
    }, 8000);

    var flashSuccess = document.querySelector('.flash-message.success');
    if (flashSuccess) {
        document.getElementById('successMetricsButton').style.display = 'block';
        document.getElementById('closeButton').style.display = 'block';
    }
});

function hideSuccessMetricsButton() {
    document.getElementById('successMetricsButton').style.display = 'none';
    document.getElementById('closeButton').style.display = 'none';
}
