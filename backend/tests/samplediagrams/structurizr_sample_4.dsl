workspace {
  model {
    user = person "User"
    app = softwareSystem "Mobile App" {
      ui = container "UI"
      api = container "API"
      user -> ui "Uses"
      ui -> api "Calls"
    }
  }
  views {
    container app {
      include *
      autolayout lr
    }
  }
}