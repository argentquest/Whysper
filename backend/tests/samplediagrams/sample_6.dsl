workspace {
  model {
    visitor = person "Visitor"
    cms = softwareSystem "Content Management System" {
      site = container "Website"
      editor = container "Content Editor"
      storage = container "Storage"
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