/* Live resume page.
 *
 * On load and on every click of "Download PDF" it reads current AetherGrid
 * figures from GitHub. If a figure cannot be read, it falls back to the last
 * saved value in ../stats/stats.json and says so. It never prints a blank or
 * invented number.
 */
(function () {
  "use strict";

  var OWNER = "wycliffRotich-dev";
  var REPO = "aethergrid";
  var TEST_BADGE =
    "https://gist.githubusercontent.com/wycliffRotich-dev/" +
    "4b35dff5cea5aa68433713c36c3108bb/raw/aethergrid-test-badge.json";
  var ADR_LIST = "https://api.github.com/repos/" + OWNER + "/" + REPO + "/contents/docs/adr";
  var REPO_URL = "https://github.com/" + OWNER + "/" + REPO;

  var data = null;
  var stats = null;

  function $(id) {
    return document.getElementById(id);
  }

  function sane(n) {
    return typeof n === "number" && isFinite(n) && Math.floor(n) === n && n > 0 && n < 1000000;
  }

  function fetchJson(url, ms) {
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, ms || 8000);
    return fetch(url, { signal: ctrl.signal, cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .finally(function () { clearTimeout(timer); });
  }

  function liveTests() {
    return fetchJson(TEST_BADGE + "?t=" + Date.now()).then(function (d) {
      var m = /\d+/.exec(String((d && d.message) || ""));
      return m ? parseInt(m[0], 10) : null;
    });
  }

  function liveAdrs() {
    return fetchJson(ADR_LIST).then(function (items) {
      return items.filter(function (i) { return /^\d{4}-.*\.md$/.test(i.name); }).length;
    });
  }

  // Returns {tests:{value,source}, adrs:{value,source}, allLive, fetchedAt}
  function getStats() {
    var saved = fetchJson("../stats/stats.json").catch(function () { return {}; });
    return Promise.all([
      liveTests().catch(function () { return null; }),
      liveAdrs().catch(function () { return null; }),
      saved
    ]).then(function (res) {
      var out = { fetchedAt: new Date() };
      var keys = ["tests", "adrs"];
      for (var i = 0; i < keys.length; i++) {
        var k = keys[i];
        var live = res[i];
        var old = res[2][k];
        if (sane(live)) out[k] = { value: live, source: "live" };
        else if (sane(old)) out[k] = { value: old, source: "saved" };
        else throw new Error("Could not get a trustworthy value for " + k);
      }
      out.allLive = out.tests.source === "live" && out.adrs.source === "live";
      return out;
    });
  }

  function plain(s) {
    return { tests: s.tests.value, adrs: s.adrs.value };
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function addInline(node, str) {
    ResumePdf.inline(str, plain(stats)).forEach(function (run) {
      if (run.bold) node.appendChild(el("strong", null, run.text));
      else node.appendChild(document.createTextNode(run.text));
    });
  }

  function pipes(s) {
    return String(s).replace(/\s*\|\s*/g, " | ");
  }

  function section(title) {
    var s = el("section", "block");
    s.appendChild(el("h2", null, title));
    return s;
  }

  function render() {
    var root = $("resume");
    root.textContent = "";

    // Header
    var head = el("header", "head");
    head.appendChild(el("h1", null, data.name));
    head.appendChild(el("p", "headline", pipes(data.headline)));
    head.appendChild(el("p", "avail", data.availability.join(" | ")));
    data.contact_rows.forEach(function (row) {
      var p = el("p", "contact");
      row.forEach(function (item, i) {
        if (i) p.appendChild(el("span", "sep", " | "));
        if (item[1]) {
          var a = el("a", null, item[0]);
          a.href = item[1];
          a.rel = "noopener";
          p.appendChild(a);
        } else {
          p.appendChild(document.createTextNode(item[0]));
        }
      });
      head.appendChild(p);
    });
    root.appendChild(head);

    // Key numbers
    var grid = el("div", "metrics");
    data.metrics.forEach(function (m) {
      var card = el("div", "metric");
      card.appendChild(el("div", "value", ResumePdf.fill(m.value, plain(stats))));
      card.appendChild(el("div", "label", m.label));
      if (m.live && stats[m.live]) {
        card.appendChild(
          el("div", "badge " + stats[m.live].source, stats[m.live].source === "live" ? "live" : "saved copy")
        );
      }
      grid.appendChild(card);
    });
    root.appendChild(grid);

    // Summary
    var sum = section("Professional Summary");
    var sp = el("p", "summary");
    addInline(sp, data.summary);
    sum.appendChild(sp);
    root.appendChild(sum);

    // Skills
    var sk = section("Technical Skills");
    var dl = el("dl", "skills");
    data.skills.forEach(function (row) {
      dl.appendChild(el("dt", null, row[0]));
      dl.appendChild(el("dd", null, row[1]));
    });
    sk.appendChild(dl);
    root.appendChild(sk);

    // Experience
    var ex = section("Professional Experience");
    data.experience.forEach(function (job) {
      var j = el("article", "job");
      var top = el("div", "jobtop");
      top.appendChild(el("h3", null, job.title));
      top.appendChild(el("span", "dates", job.dates));
      j.appendChild(top);
      j.appendChild(el("p", "org", pipes(job.org)));
      var ul = el("ul");
      job.bullets.forEach(function (b) {
        var li = el("li");
        addInline(li, b);
        ul.appendChild(li);
      });
      j.appendChild(ul);
      ex.appendChild(j);
    });
    root.appendChild(ex);

    // Education
    var ed = section("Education");
    data.education.forEach(function (e) {
      var j = el("article", "job");
      var top = el("div", "jobtop");
      top.appendChild(el("h3", null, e.title));
      top.appendChild(el("span", "dates", e.dates));
      j.appendChild(top);
      j.appendChild(el("p", "org", e.school));
      ed.appendChild(j);
    });
    root.appendChild(ed);

    renderStatus();
  }

  function renderStatus() {
    var box = $("status");
    var t = stats.tests;
    var a = stats.adrs;
    var line = "AetherGrid figures: " + t.value + " tests (" + t.source + "), " +
      a.value + " ADRs (" + a.source + "). ";
    if (stats.allLive) {
      line += "Read from GitHub just now. The test count is from the last passing CI run on main.";
      box.className = "status ok";
    } else {
      line += "Some figures could not be read live, so the last saved copy is shown. Reload to try again.";
      box.className = "status warn";
    }
    box.textContent = line;
  }

  function stamp(d) {
    return d.toISOString().slice(0, 16).replace("T", " ") + " UTC";
  }

  function download() {
    var btn = $("download");
    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = "Fetching current figures...";
    return getStats()
      .then(function (fresh) {
        stats = fresh;
        render();
        if (!fresh.allLive) {
          var ok = window.confirm(
            "Live figures could not be read, so the PDF will use the last saved numbers (" +
              fresh.tests.value + " tests, " + fresh.adrs.value + " ADRs). Download anyway?"
          );
          if (!ok) return null;
        }
        var doc = ResumePdf.buildDocDefinition(data, plain(fresh), {
          asOf: fresh.allLive ? stamp(fresh.fetchedAt) : null
        });
        var file = data.name.replace(/\s+/g, "_") + "_Resume.pdf";
        return pdfMake.createPdf(doc).download(file);
      })
      .catch(function (err) {
        window.alert("Could not build the PDF: " + err.message);
      })
      .finally(function () {
        btn.disabled = false;
        btn.textContent = label;
      });
  }

  function init() {
    $("repo-link").href = REPO_URL;
    Promise.all([fetchJson("../resume.json"), getStats()])
      .then(function (res) {
        data = res[0];
        stats = res[1];
        render();
        $("download").disabled = false;
        $("download").addEventListener("click", download);
      })
      .catch(function (err) {
        $("resume").textContent = "Could not load the resume: " + err.message;
      });
  }

  init();
})();
