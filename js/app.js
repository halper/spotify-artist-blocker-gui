var ctx = $("#myChart");
var myRadarChart;

function initMyChart(labels, data) {
    myRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Interest",
                    backgroundColor: "rgba(179,181,198,0.2)",
                    borderColor: "rgba(179,181,198,1)",
                    pointBackgroundColor: "rgba(179,181,198,1)",
                    pointBorderColor: "#fff",
                    pointHoverBackgroundColor: "#fff",
                    pointHoverBorderColor: "rgba(179,181,198,1)",
                    data: data
                }
            ]
        },
        options: {
            responsive: true,
            scale: {
                reverse: false,
                ticks: {
                    beginAtZero: true,
                    display: false
                }
            }
        }
    });
}

function updateRenderChart() {
    myRadarChart.update();
    myRadarChart.render();
}

var vm = new Vue({
    el: '#app',
    data: {
        currentSong: [],
        cTitle: '',
        cArtist: '',
        cAlbum: '',
        cCover: '',
        songs: [],
        chartInit: false,
        currentPage: 1,
        lastPage: 2
    },
    http: {
        emulateJSON: true,
        emulateHTTP: true
    },
    ready: function () {
        this.fetchMyData(this.currentPage);
    },
    methods: {
        fetchMyData: function (currentPage) {
            if (currentPage >= 1 && currentPage <= this.lastPage) {
                this.$http.post('my-spotify-data.php', {
                    page: currentPage
                }).then(function (response) {
                    this.currentSong = response.data.currentSong;
                    this.currentPage = currentPage;
                    this.lastPage = response.data.last_page;
                    /*this.cTitle = response.data.cTitle;
                    this.cArtist = response.data.cArtist;
                    this.cAlbum = response.data.cAlbum;
                    this.cCover = response.data.cCover;*/
                    this.songs = response.data.songs;
                    if (!this.chartInit) {
                        this.chartInit = true;
                        initMyChart(response.data.genres, response.data.data)
                    }
                    else {
                        myRadarChart.data.datasets[0].data = response.data.data;
                        updateRenderChart();
                    }
                });
            }
        },
        restrictArtist: function (id) {
            this.$http.post('spotify-action.php', {
                    id: id
                })
                .then(function (response) {
                    if (response.data === 'success') this.fetchMyData(this.currentPage);
                });
        }
    }
});

Vue.filter('wholeSrc', function (value) {
    return 'https://open.spotify.com/image/' + value
});

Vue.filter('times', function (value) {
    return value + (value > 1 ? ' times' : ' time');
});

Vue.filter('duration', function (value) {
    var duration = Math.floor(value / 1000000);
    return Math.floor(duration / 60) + ':' + Math.floor(duration % 60);
});

Vue.filter('timeConverter', function (value, count) {
    var totalDuration = Math.floor(value / 1000000) * count;
    var seconds = Math.floor(totalDuration % 60);
    var minutes = Math.floor(totalDuration / 60);
    var hours = Math.floor(minutes / 60);
    var days = Math.floor(hours / 24);
    var weeks = Math.floor(days / 7);
    var months = Math.floor(days / 30);
    var years = Math.floor(days / 365);
    var length = '';
    if (years > 0) length = length + years + (years > 1 ? " years " : " year ");
    if (months > 0) length = length + months + (months > 1 ? " months " : " month ");
    if (weeks > 0) length = length + weeks + (weeks > 1 ? " weeks " : " week ");
    if (days > 0) length = length + days + (days > 1 ? " days " : " day ");
    if (hours > 0) length = length + hours + (hours > 1 ? " hours " : " hour ");
    if (minutes > 0) length = length + minutes + (minutes > 1 ? " minutes " : " minute ");
    if (seconds > 0) length = length + seconds + (seconds > 1 ? " seconds " : " second ");
    return length;
});


setInterval(function () {
    vm.fetchMyData(vm.currentPage);
}, 25000);



