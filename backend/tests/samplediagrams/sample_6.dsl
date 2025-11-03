workspace {
  model {
    visitor = person "Visitor"
    cms = softwareSystem "Content Management System" {
      container site "Website"
      container editor "Content Editor"
      container storage "Storage"
      visitor -> site "Views"
      editor -> storage "Saves content"
    }
  }
  views {
    container cms {
      include *
      autolayout lr
    }
  }
}