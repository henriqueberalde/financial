const SVG_NS = "http://www.w3.org/2000/svg";

function assign(element, attributes) {
  for (const [name, value] of Object.entries(attributes)) {
    if (value == null || value === false) continue;
    if (name.startsWith("on")) {
      element.addEventListener(name.slice(2).toLowerCase(), value);
    } else if (name === "style") {
      Object.assign(element.style, value);
    } else {
      element.setAttribute(name === "className" ? "class" : name,
                           value === true ? "" : value);
    }
  }
}

function append(element, children) {
  for (const child of children.flat(Infinity)) {
    if (child == null || child === false) continue;
    // Strings become text nodes, so data is never parsed as HTML
    element.append(child instanceof Node ? child : String(child));
  }
}

export function h(tag, attributes = {}, ...children) {
  const element = document.createElement(tag);
  assign(element, attributes);
  append(element, children);
  return element;
}

export function s(tag, attributes = {}, ...children) {
  const element = document.createElementNS(SVG_NS, tag);
  assign(element, attributes);
  append(element, children);
  return element;
}
