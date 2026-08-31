const DATA_PATH = "data";
const PAGE_SIZE = 5;

const el = (id) => document.getElementById(id);

async function loadJson(name) {
  const response = await fetch(`${DATA_PATH}/${name}`);
  if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
  return response.json();
}

async function loadJsonLines(name) {
  const response = await fetch(`${DATA_PATH}/${name}`);
  if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
  const text = await response.text();
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function addText(parent, text, className) {
  const span = document.createElement("span");
  span.className = className;
  span.textContent = text;
  parent.append(span);
}

function formatTimestamp(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function renderPagedList(id, items, renderItem) {
  const list = el(id);
  const controls = el(`${id}-pagination`);
  const previous = controls.querySelector("[data-previous]");
  const next = controls.querySelector("[data-next]");
  const label = controls.querySelector("[data-page]");
  const pageCount = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  let page = 0;

  function render() {
    list.replaceChildren();
    const pageItems = items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
    if (pageItems.length === 0) {
      const item = document.createElement("li");
      item.className = "muted";
      item.textContent = "none yet";
      list.append(item);
    } else {
      pageItems.forEach((value) => {
        const item = document.createElement("li");
        renderItem(item, value);
        list.append(item);
      });
    }
    label.textContent = `Page ${page + 1} of ${pageCount}`;
    previous.disabled = page === 0;
    next.disabled = page + 1 === pageCount;
  }

  previous.addEventListener("click", () => { page -= 1; render(); });
  next.addEventListener("click", () => { page += 1; render(); });
  render();
}

function renderMeta(status) {
  const meta = el("meta");
  const link = document.createElement("a");
  link.href = status.channel.url;
  link.textContent = status.channel.handle;
  meta.append(link, " - updated ");
  const time = document.createElement("time");
  time.dateTime = status.updated_at;
  time.textContent = formatTimestamp(status.updated_at);
  meta.append(time);

  el("goal").textContent = `Goal: ${status.goal}`;
  Object.entries(status.stats).forEach(([key, value]) => {
    const stat = document.createElement("div");
    stat.className = "stat";
    const number = document.createElement("b");
    number.textContent = value.toLocaleString();
    stat.append(number, key.replace("_usd", " ($)"));
    el("stats").append(stat);
  });
}

async function main() {
  const [status, slate, log] = await Promise.all([
    loadJson("status.json"),
    loadJson("slate.json"),
    loadJsonLines("log.jsonl"),
  ]);

  renderMeta(status);
  const slateNewestFirst = slate
    .filter((entry) => entry.date)
    .reverse()
    .concat(slate.filter((entry) => !entry.date));
  renderPagedList("slate", slateNewestFirst, (item, entry) => {
    if (entry.date) addText(item, `${entry.date} `, "date");
    if (entry.url) {
      const link = document.createElement("a");
      link.href = entry.url;
      link.textContent = entry.title;
      item.append(link);
    } else {
      item.append(entry.title);
    }
    addText(item, ` [${entry.status}]`, "tag");
    if (entry.views !== undefined) addText(item, ` ${entry.views} views`, "tag");
    if (entry.note) addText(item, ` [${entry.note}]`, "tag");
  });
  renderPagedList("log", [...log].reverse(), (item, event) => {
    const time = document.createElement("time");
    time.className = "date";
    time.dateTime = event.timestamp;
    time.textContent = formatTimestamp(event.timestamp);
    item.append(time, event.entry);
  });
}

main().catch((error) => {
  el("error").textContent = `Could not load status data: ${error.message}`;
});
