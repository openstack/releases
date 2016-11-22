// Toggle main sections
$(".docs-sidebar-section-title").click(function () {
    $('.docs-sidebar-section').not(this).closest('.docs-sidebar-section').removeClass('active');
    $(this).closest('.docs-sidebar-section').toggleClass('active');
// Bug #1422454
// Commenting out next line, the default behavior which was preventing links
// from working.
//    event.preventDefault();
});

/* Bug #1422454
   The toggle functions below enable the expand/collapse, but for now
   there's no easy way to get deeper links from other guides. So,
   commenting both toggle functions out.
// Toggle 1st sub-sections
$(".docs-sidebar-section ol lh").click(function () {
    $('.docs-sidebar-section ol').not(this).closest('.docs-sidebar-section ol').removeClass('active');
    $(this).closest('.docs-sidebar-section ol').toggleClass('active');
    if ($('.docs-has-sub').hasClass('active')) {
      $(this).closest('.docs-sidebar-section ol li').addClass('open');
    }
    event.preventDefault();
});

// Toggle 2nd sub-sections
$(".docs-sidebar-section ol > li > a").click(function () {
    $('.docs-sidebar-section ol li').not(this).removeClass('active').removeClass('open');
    $(this).closest('.docs-sidebar-section ol li').toggleClass('active');
    if ($('.docs-has-sub').hasClass('active')) {
      $(this).closest('.docs-sidebar-section ol li').addClass('open');
    }
    event.preventDefault();
});

/* Bug #1417291
   The rule below creates a shaded plus sign next to
   a numbered sublist of a bulleted list.
   It's probably there to implement expand/collapse of
   list items, but unfortunately it affects also those
   lists where expand/collapse is not intended.

   I am commenting it out to fix this bug. If it causes
   problems elsewhere, they have to be fixed elsewhere. */

// $('ol > li:has(ul)').addClass('docs-has-sub');

// webui popover
$(document).ready(function() {
    function checkWidth() {
        var windowSize = $(window).width();

        if (windowSize <= 767) {
            $('.gloss').webuiPopover({placement:'auto',trigger:'click'});
        }
        else if (windowSize >= 768) {
            $('.gloss').webuiPopover({placement:'auto',trigger:'hover'});
        }
    }

    // Execute on load
    checkWidth();
    // Bind event listener
    $(window).resize(checkWidth);
});

// Bootstrap stuff
$('.docs-actions i').tooltip();
$('.docs-sidebar-home').tooltip();

// Hide/Toggle definitions
$("#toggle-definitions").click(function () {
  $(this).toggleClass('docs-info-off');
  if ($('.gloss').hasClass('on')) {
      $('.gloss').removeClass('on').addClass('off').webuiPopover('destroy');
  } else if ($('.gloss').hasClass('off')) {
      $('.gloss').removeClass('off').addClass('on').webuiPopover();
  }
});

/* BB 150310
   openstackdocstheme provides three types of admonitions, important, note
   and warning. We decorate their title paragraphs with Font Awesome icons
   by adding the appropriate FA classes.                               */

$('div.important > p.admonition-title').addClass('fa fa-info-circle');
$('div.note > p.admonition-title').addClass('fa fa-check-circle');
$('div.warning > p.admonition-title').addClass('fa fa-exclamation-triangle');

/* BB 150310
   We also insert a space between the icon and the admonition title
   ("Note", "Warning", "Important" or their i18n equivalents).

   This could be done with a single clause $('p.admonition-title')....,
   affecting all types of admonitions. I play it safe here and explicitly
   work on the three openstackdocstheme admonitions.

   The first parameter of the text() callback is not needed here (it's
   the index of the HTML element that we are modifying)                 */

$('div.important > p.admonition-title').text(function(ignored_para,original) {
    return " "+original
});
$('div.note > p.admonition-title').text(function(ignored_para,original) {
    return " "+original
});
$('div.warning > p.admonition-title').text(function(ignored_para,original) {
    return " "+original
});
