// Typst template for the hiking report PDF.
// Reads images/images_recap.csv (columns: filename, localite_depart, date).
// Produces one page per hike with the map image, starting locality, and date.
// Ends with a table of contents and an alphabetical locality index with page numbers.

// Load CSV data
#let raw-data = csv("images/images_recap.csv")

// Convert rows to dictionaries keyed by header name
#let data = {
  let headers = raw-data.at(0)
  raw-data.slice(1).map(row => {
    let entry = (:)
    for (i, header) in headers.enumerate() {
      entry.insert(header, row.at(i))
    }
    entry
  })
}

// Global page style
#set page(numbering: "1", margin: 1.5cm)
#set heading(numbering: none)

// Headings: centred and bold
#show heading.where(level: 1): it => align(center)[#text(it.body, weight: "bold", size: 16pt)]

// Render one hike page: heading + centred map image
#let page-image(entry) = [
  #let file = entry.at("filename")
  #let loc = entry.at("localite_depart")
  #let date = entry.at("date")

  #heading(level: 1, loc + " — " + date)
  
  #v(0.8em)
  #align(center)[
    #image("images/" + file, width: 85%, fit: "contain")
  ]

  #pagebreak()
]

// Generate one page per hike
#for entry in data {
  page-image(entry)
}

// Table des matières
= Table des matières
#outline()

= Index des localités

#context {
  // Headings are generated in the same order as data entries,
  // so we can zip them to retrieve page numbers.
  let headings = query(heading.where(level: 1))
  let index = (:)
  for (i, entry) in data.enumerate() {
    let loc_name = entry.at("localite_depart")
    let page_num = str(headings.at(i).location().page())
    let pages = if loc_name in index { index.at(loc_name) + ", " + page_num } else { page_num }
    index.insert(loc_name, pages)
  }
  for loc_name in index.keys().sorted() {
    grid(
      columns: (1fr, auto),
      loc_name,
      align(right, index.at(loc_name))
    )
  }
}