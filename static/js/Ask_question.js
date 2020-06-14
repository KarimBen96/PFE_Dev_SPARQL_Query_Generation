var app_10 = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app_10',
    data: {
        firstname: 'Karim'
    }
})

var app_3 = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app_3',
    data: {
        items: ['Definition', 'Yes / No'],
        firstname: 'Karim'
    }
})


new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        message: 'Hello Vue!'
    }
})