"use strict";

// Auto save comment form
function autoSaveComment() {
    var timeoutId;
    $('#add-comment .wysihtml5-sandbox').contents().find('body').on('input properychange change', function () {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(function () {
            $('#add-comment').ajaxForm({
                beforeSubmit: function (arr, form) {
                    if (!comment_editor.getValue()) {
                        return false;
                    }
                    $('.add-comment-btn').prop('disabled', true);
                    $('#comment-status').html(gettext('Saving...'));
                },
                data: {
                    'comment_id': $('#add-comment').data('comment-id')
                },
                success: function (data) {
                    $('#add-comment').data('comment-id', data.comment_id);
                    var d = new Date();
                    $('#comment-status').html(gettext('Saved! Last:') + ' ' + d.toLocaleTimeString('he-IL'));
                    $('.add-comment-btn').prop('disabled', false);
                }
            });
            $('#add-comment').submit();
        }, 2000);
    });
}

// Auto save reference form
function autoSaveReference() {
    var timeoutId;
    $('#add-reference .wysihtml5-sandbox').contents().find('body').on('input properychange change', function () {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(function () {
            $('#add-reference').ajaxForm({
                beforeSubmit: function (arr, form) {
                    if (!reference_editor.getValue()) {
                        return false;
                    }
                    $('.add-reference-btn').prop('disabled', true);
                    $('#reference-status').html(gettext('Saving...'));
                },
                data: {
                    'reference_id': $('#add-reference').data('reference-id'),
                    'is_reference': true
                },
                success: function (data) {
                    $('#add-reference').data('reference-id', data.reference_id);
                    var d = new Date();
                    $('#reference-status').html(gettext('Saved! Last:') + ' ' + d.toLocaleTimeString('he-IL'));
                    $('.add-reference-btn').prop('disabled', false);
                }
            });
            $('#add-reference').submit();
        }, 2000);
    });
}

let comment_editor;
let reference_editor;

$(function () {

    function refreshButtons1(commentEmpty) {
        $('.add-comment-btn').prop('disabled', commentEmpty);
    }

    function refreshButtons2(commentEmpty) {
        $('.add-reference-btn').prop('disabled', commentEmpty);
        $('.close-issue-btn').prop('disabled', !commentEmpty);
    }

    if ($('#add-comment .htmlarea textarea').length) {
        comment_editor = $('#add-comment .htmlarea textarea').ocdEditor().data('wysihtml5').editor;

        comment_editor.on('input', function () {
            refreshButtons1(comment_editor.getValue().trim() == '');
        });
    }

    if ($('#add-reference .htmlarea textarea').length) {
        reference_editor = $('#add-reference .htmlarea textarea').ocdEditor().data('wysihtml5').editor;

        reference_editor.on('input', function () {
            refreshButtons2(reference_editor.getValue().trim() == '');
        });
    }

    // Comments

    $('body').on('click', '.add-comment-btn', function () {
        var nextIssue = $(this).data('next-issue');
        $('#add-comment').ajaxForm({
            beforeSubmit: function (arr, form) {
                if (!comment_editor.getValue()) {
                    return false;
                }
            },
            data: {
                'comment_id': $('#add-comment').data('comment-id')
            },
            success: function (data) {
                window.location.href = nextIssue;
            }
        });
    });

    // References

    $('body').on('click', '.add-reference-btn', function () {
        var nextIssue = $(this).data('next-issue');
        $('#add-reference').ajaxForm({
            beforeSubmit: function (arr, form) {
                if (!reference_editor.getValue()) {
                    return false;
                }
            },
            data: {
                'reference_id': $('#add-reference').data('reference-id'),
                'is_reference': true
            },
            success: function (data) {
                window.location.href = nextIssue;
            }
        });
    });

//    // Add comment form
//    $('#add-comment').ajaxForm({
//        beforeSubmit: function (arr, form) {
//            if (!$('#id_content').val()) {
//                return false;
//            }
//        },
//        success: function (data) {
//            var el = $(data.trim());
//            $("#add-comment").closest('li').before(el);
//            $("#add-comment").get(0).reset();
//            refreshButtons(true);
//        }
//    });

    // Delete and undelete comment form
    $('#comments').on('click', '.delete-comment button', function () {
        var btn = $(this);
        var form = btn.closest('form');
        var extra = {};
        if (btn.attr('name')) {
            extra[btn.attr('name')] = btn.attr('value');
        }
        form.ajaxSubmit({
            data: extra,
            success: function (data) {
                form.closest('li').toggleClass('deleted', data == '0');
            }
        });
        return false;
    });

    // Delete and undelete reference form
    $('#references').on('click', '.delete-reference button', function () {
        var btn = $(this);
        var form = btn.closest('form');
        var extra = {};
        if (btn.attr('name')) {
            extra[btn.attr('name')] = btn.attr('value');
        }
        form.ajaxSubmit({
            data: extra,
            success: function (data) {
                form.closest('li').toggleClass('deleted', data == '0');
            }
        });
        return false;
    });

    // Edit comment Form:

    //  - start edit
    $('#comments').on('click', '.edit-comment button', function () {
        $('#comments li.rich_editor').hide();
        var btn = $(this);
        var li = btn.closest('li');
        li.addClass('editing');
        var el = $("<div>Loading...</div>");
        li.find('.comment-inner').hide().after(el);
        $.get(btn.data('url'), function (data) {
            el.html(data).find('.htmlarea textarea').wysihtml5({locale: "he-IL"});
        });
    });

    // - cancel edit
    $('#comments').on('click', '.cancel-edit-comment button', function () {
        $('#comments li.rich_editor').show();
        var btn = $(this);
        var li = btn.closest('li');
        li.removeClass('editing');
        li.find('.comment-inner').show();
        li.find('.edit-issue-form').parent().remove();
    });

    // - save edits
    $('#comments').on('click', '.save-comment button', function (ev) {
        $('#comments li.rich_editor').show();
        var btn = $(this);
        var form = btn.closest('form');
        if (!form.find('textarea').val()) {
            ev.preventDefault();
            return false;
        }
        form.ajaxSubmit(function (data) {
            if (!data) {
                return;
            }
            var new_li = $(data.trim());
            form.closest('li').replaceWith(new_li);
        });
        return false;
    });

    // Edit reference Form:

    //  - start edit
    $('#references').on('click', '.edit-reference button', function () {
        $('#references li.rich_editor').hide();
        var btn = $(this);
        var li = btn.closest('li');
        li.addClass('editing');
        var el = $("<div>Loading...</div>");
        li.find('.reference-inner').hide().after(el);
        $.get(btn.data('url'), function (data) {
            el.html(data).find('.htmlarea textarea').wysihtml5({locale: "he-IL"});
        });
    });

    // - cancel edit
    $('#references').on('click', '.cancel-edit-reference button', function () {
        $('#references li.rich_editor').show();
        var btn = $(this);
        var li = btn.closest('li');
        li.removeClass('editing');
        li.find('.reference-inner').show();
        li.find('.edit-issue-form').parent().remove();
    });

    // - save edits
    $('#references').on('click', '.save-reference button', function (ev) {
        $('#references li.rich_editor').show();
        var btn = $(this);
        var form = btn.closest('form');
        if (!form.find('textarea').val()) {
            ev.preventDefault();
            return false;
        }
        form.ajaxSubmit(function (data) {
            if (!data) {
                return;
            }
            var new_li = $(data.trim());
            form.closest('li').replaceWith(new_li);
        });
        return false;
    });

    $('#issue-complete,#issue-archive').ajaxForm({
        success: function (data) {
            var target = window.location.protocol + '//' + window.location.host + window.location.pathname;
            window.location = target;
            // window.history.back();
        }
    });

    $('#issue-undo-complete').ajaxForm({
        success: function (data) {
            location.reload();
            // var target = window.location.protocol + '//' + window.location.host + window.location.pathname;
            // window.location = target;
        }

    });

    // fill empty file title upon file selection
    $('body').on('change', 'input#id_file', function () {
        var title_inp = $(this).closest('form').find('input#id_title');
        if (title_inp.val().length > 0)
            return;
        var full_filename = $(this).val();
        var base_filename = '';
        title_inp.val(base_filename);
    });

    // Edit issue confidential approval
    $('#issue_edit_submit').on('click', function () {
        $(this).popover('show');
    })

});

$(window).load(function () {
    autoSaveComment();
    // autoSaveReference();
});
