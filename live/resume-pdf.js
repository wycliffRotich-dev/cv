/* Builds the pdfmake document definition from resume.json plus current stats.
 *
 * Plain text only: one column, no tables, no images, real fonts. That is what
 * applicant tracking systems read best.
 *
 * Works in the browser (window.ResumePdf) and in Node (module.exports) so the
 * same code can be tested outside a browser.
 */
(function (root) {
  "use strict";

  var ACCENT = "#1f4e79";
  var MUTED = "#555555";
  var TEXT = "#1c1c1c";
  var CONTENT_WIDTH = 515; // A4 width 595 minus 40 pt margins on each side

  // Replace {{name}} markers. A marker with no value is an error: the PDF must
  // never go out with a blank or made-up number.
  function fill(str, stats) {
    return String(str).replace(/\{\{(\w+)\}\}/g, function (_m, key) {
      var v = stats ? stats[key] : undefined;
      if (v === undefined || v === null || v === "") {
        throw new Error("No value for {{" + key + "}}");
      }
      return String(v);
    });
  }

  // Split a string with <b>...</b> into runs: [{text}, {text, bold:true}, ...]
  function inline(str, stats) {
    var s = fill(str, stats);
    var out = [];
    var re = /<b>(.*?)<\/b>/g;
    var last = 0;
    var m;
    while ((m = re.exec(s))) {
      if (m.index > last) out.push({ text: s.slice(last, m.index) });
      out.push({ text: m[1], bold: true });
      last = re.lastIndex;
    }
    if (last < s.length) out.push({ text: s.slice(last) });
    return out;
  }

  function tidyPipes(s) {
    return String(s).replace(/\s*\|\s*/g, " | ");
  }

  function heading(title) {
    return [
      { text: title.toUpperCase(), style: "section" },
      {
        canvas: [
          { type: "line", x1: 0, y1: 0, x2: CONTENT_WIDTH, y2: 0, lineWidth: 0.8, lineColor: ACCENT }
        ],
        margin: [0, 2, 0, 5]
      }
    ];
  }

  function buildDocDefinition(data, stats, opts) {
    opts = opts || {};
    var content = [];

    content.push({ text: data.name, style: "name" });
    content.push({ text: tidyPipes(data.headline), style: "headline" });
    content.push({ text: data.availability.join(" | "), style: "avail" });

    data.contact_rows.forEach(function (row) {
      var parts = [];
      row.forEach(function (item, i) {
        if (i) parts.push({ text: " | ", color: MUTED });
        var run = { text: item[0] };
        if (item[1]) {
          run.link = item[1];
          run.color = ACCENT;
        }
        parts.push(run);
      });
      content.push({ text: parts, style: "contact" });
    });

    // Key numbers as one line of plain text, not a table or columns.
    var mparts = [];
    data.metrics.forEach(function (m, i) {
      if (i) mparts.push({ text: "   |   ", color: MUTED });
      mparts.push({ text: fill(m.value, stats), bold: true, color: ACCENT });
      mparts.push({ text: " " + m.label });
    });
    content.push({ text: mparts, style: "metrics" });

    content.push.apply(content, heading("Professional Summary"));
    content.push({ text: inline(data.summary, stats), style: "body" });

    content.push.apply(content, heading("Technical Skills"));
    data.skills.forEach(function (row) {
      content.push({
        text: [{ text: row[0] + ": ", bold: true }, { text: row[1] }],
        style: "body",
        margin: [0, 0, 0, 2]
      });
    });

    content.push.apply(content, heading("Professional Experience"));
    data.experience.forEach(function (job) {
      content.push({ text: job.title, style: "role" });
      content.push({ text: tidyPipes(job.org) + " | " + job.dates, style: "orgline" });
      content.push({
        ul: job.bullets.map(function (b) {
          return { text: inline(b, stats), style: "body", margin: [0, 0, 0, 1.5] };
        }),
        markerColor: ACCENT,
        margin: [0, 2, 0, 0]
      });
    });

    content.push.apply(content, heading("Education"));
    data.education.forEach(function (e) {
      content.push({ text: e.title, style: "role" });
      content.push({ text: e.school + " | " + e.dates, style: "orgline" });
    });

    var doc = {
      content: content,
      pageSize: "A4",
      pageMargins: [40, 38, 40, 46],
      info: {
        title: data.name + " - Resume",
        author: data.name,
        subject: "Platform engineer resume"
      },
      defaultStyle: { font: "Roboto", fontSize: 9.8, lineHeight: 1.22, color: TEXT },
      styles: {
        name: { fontSize: 24, bold: true, color: "#111111", margin: [0, 0, 0, 1] },
        headline: { fontSize: 11.5, bold: true, color: ACCENT, margin: [0, 0, 0, 2] },
        avail: { fontSize: 9.5, color: MUTED, margin: [0, 0, 0, 2] },
        contact: { fontSize: 9.5, color: TEXT, margin: [0, 0, 0, 1] },
        metrics: { fontSize: 9.5, margin: [0, 7, 0, 0] },
        section: { fontSize: 10.5, bold: true, color: ACCENT, characterSpacing: 0.8, margin: [0, 11, 0, 0] },
        role: { fontSize: 10.5, bold: true, margin: [0, 6, 0, 0] },
        orgline: { fontSize: 9.5, color: MUTED, margin: [0, 0, 0, 1] },
        body: {}
      }
    };

    if (opts.asOf) {
      doc.footer = function () {
        return {
          text: "AetherGrid figures fetched from GitHub on " + opts.asOf,
          fontSize: 8,
          color: MUTED,
          alignment: "center",
          margin: [40, 14, 40, 0]
        };
      };
    }
    return doc;
  }

  var api = { fill: fill, inline: inline, buildDocDefinition: buildDocDefinition };
  root.ResumePdf = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
