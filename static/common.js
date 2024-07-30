// Shamelessly stolen from https://github.com/vakata/jstree/issues/1101
(function ($, _) {
    "use strict";
    $.jstree.plugins.noclose = function () {
        this.close_node = $.noop;
    };
})(jQuery);

addEventListener("DOMContentLoaded", (event) => {
    let trees = $('.tree');

    for (let tree of trees) {
        $(tree).jstree({
            "core": {
                "themes": {
                    "icons": false
                },
            },
            "plugins": ["checkbox", "themes", "noclose"]
        });

        // Open all
        $(tree).on('ready.jstree', function () {
            $(tree).jstree('open_all');
        });

        // Select all
        // $(tree).on('ready.jstree', function () {
        //     $(tree).jstree('select_all');
        // });
    }
});

// Display an error message for the query form
function displayErrorQuery(message) {
    $('#error').text(message);
    $('#error').show();
}

// Display an error message for the article form
function displayErrorArticle(message) {
    $('#error-article').text(message);
    $('#error-article').show();
}

// number or number-number
const wavenumber_regex = new RegExp('\\s*\\d+(\\s*-\\s*\\d+)?\\s*$');

function submitFormQuery() {
    let wavenumber = $('#wavenumber').val();
    let window_size = $('#window-size').val();
    let keywords = $('#keywords').val();
    let attributions = $('#attributions').val();
    let species = $('#species').jstree('get_selected');
    let samples = $('#samples').jstree('get_selected');
    let metadata = $('#metadata').val();

    // Validation
    // Make sure wavenumber matches the regex if it ain't empty or full of whitespace
    if (wavenumber.trim() !== '') {
        if (!wavenumber_regex.test(wavenumber)) {
            displayErrorQuery('Invalid wavenumber');
            return;
        }
    } else {
        displayErrorQuery('Please enter a wavenumber');
        return;
    }

    // Make sure there is at least one element in species or samples
    if (species.length === 0 && samples.length === 0) {
        displayErrorQuery('Please select at least one species or sample');
        return;
    }

    // Window size must be set
    if (window_size.trim() === '') {
        displayErrorQuery('Please enter a window size');
        return;
    }

    // Keywords as array (split by comma), or empty array if empty
    keywords = keywords.split(',').map(keyword => keyword.trim()).filter(keyword => keyword !== '');

    // Attributions as array (split by comma), or empty array if empty
    attributions = attributions.split(',').map(attribution => attribution.trim()).filter(attribution => attribution !== '');

    metadata = metadata.split(',').map(m => m.trim()).filter(m => m !== '');

    // Put table in loading state
    $('#query-result-table-bands').bootstrapTable('showLoading');
    $('#query-result-table-ranges').bootstrapTable('showLoading');

    $.ajax({
        dataType: 'json',
        url: '/api/spectral-search',
        data: {
            wavenumber: wavenumber,
            window_size: window_size,
            keywords: keywords,
            attributions: attributions,
            species: species,
            samples: samples,
            metadata: metadata
        },
        success: function (data) {
            // set data to the bootstrap table with id query-result-table-bands
            $('#query-result-table-bands').bootstrapTable('load', data.bands);
            $('#query-result-table-ranges').bootstrapTable('load', data.ranges);
            $('#query-result-table-bands').bootstrapTable('hideLoading');
            $('#query-result-table-ranges').bootstrapTable('hideLoading');

            // Hide the error message
            $('#error').hide();
        },
        error: function (data) {
            $('#query-result-table-bands').bootstrapTable('hideLoading');
            $('#query-result-table-ranges').bootstrapTable('hideLoading');

            // Show the error message
            displayErrorQuery('An error occurred while fetching the data');
        }
    })
}

function submitFormArticle() {
    let article = $('#article').val();

    if (article.trim() === '') {
        displayErrorArticle('Please enter an article');
        return;
    }

    // Loading state
    $('#article-result-table').bootstrapTable('showLoading');

    $.ajax({
        dataType: 'json',
        url: '/api/article-search',
        data: {
            article: article
        },
        success: function (data) {
            $('#query-result-table-articles').bootstrapTable('load', data.articles);
            $('#query-result-table-articles').bootstrapTable('hideLoading');

            // Hide the error message
            $('#error-article').hide();
        },
        error: function (data) {
            $('#query-result-table-articles').bootstrapTable('hideLoading');

            // Show the error message
            displayErrorArticle('An error occurred while fetching the data');
        }
    })
}

number_regex = new RegExp('\\d+');

// Formatter to make the article id row clickable
function article_formatter(value, row) {
    let pmcid = number_regex.exec(value)

    return `<a href="/article/${pmcid[0]}" target="_blank">${value}</a>`;
}

function print_band_table() {
    $('#query-result-table-bands').printElement();
}

function print_range_table() {
    $('#query-result-table-ranges').printElement();
}

//https://www.jqueryscript.net/other/print-element-css-divjs.html
(function ($) {
    'use strict'

    $.fn.printElement = function (options) {
        let settings = $.extend({
            title: jQuery('title').text(),
            css: 'extend',
            ecss: null,
            lcss: [],
            keepHide: [],
            wrapper: {
                wrapper: null,
                selector: null,
            }
        }, options);

        const element = $(this).clone();
        let html = document.createElement('html');

        let head = document.createElement('head');
        if (settings.title != null && settings.title != '') {
            head = $(head).append($(document.createElement('title')).text(settings.title));
        }
        else {
            head = $(head);
        }

        if (settings.css == 'extend' || settings.css == 'link') {
            $('link[rel=stylesheet]').each(function (index, linkcss) {
                head = head.append($(document.createElement('link')).attr('href', $(linkcss).attr('href')).attr('rel', 'stylesheet').attr('media', 'print'));
            })
        }

        for (var i = 0; i < settings.lcss.length; i++) {
            head = head.append($(document.createElement('link')).attr('href', settings.lcss[i]).attr('rel', 'stylesheet').attr('media', 'print'));
        }

        if (settings.css == 'extend' || settings.css == 'style') {
            head.append($(document.createElement('style')).append($('style').clone().html()));
        }

        if (settings.ecss != null) {
            head.append($(document.createElement('style')).html(settings.ecss));
        }

        if (settings.wrapper.wrapper === null) {
            var body = document.createElement('body');
            body = $(body).append(element);
        }
        else {
            var body = $(settings.wrapper.wrapper).clone();
            body.find(settings.wrapper.selector).append(element);
        }

        for (let i = 0; i < settings.keepHide.length; i++) {
            $(body).find(settings.keepHide[i]).each(function (index, data) {
                $(this).css('display', 'none');
            })
        }

        html = $(html).append(head).append(body);

        const fn_window = document.open('', settings.title, 'width=' + $(document).width() + ',height=' + $(document).width() + '');
        fn_window.document.write(html.clone().html());
        setTimeout(function () { fn_window.print(); fn_window.close() }, 250);

        return $(this);
    }
}(jQuery));

function convertToCSV(objArray) {
    const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray;
    let str = 'PMCID/Title,Wavenumber,Attribution\r\n';

    for (let i = 0; i < array.length; i++) {
        let line = '';
        line += array[i]['article_id'] + ',';
        line += array[i]['position'] + ',';
        line += array[i]['attribution'];
        str += line + '\r\n';
    }
    return str;
}

function downloadCSV() {
    const data = $('#query-result-table-bands').bootstrapTable('getData');
    const csv = convertToCSV(data);

    // Envoyer le CSV au serveur pour sauvegarde
    fetch('/save_csv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ csv: csv }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}