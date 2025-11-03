workspace {
  model {
    researcher = person "Researcher"
    dataSystem = softwareSystem "Data Analysis System" {
      ui = container "UI"
      processor = container "Data Processor"
      storage = container "Data Storage"
      researcher -> ui "Operates"
      ui -> processor "Sends tasks"
      processor -> storage "Reads/Writes"
    }
  }
  views {
    container dataSystem {
      include *
      autolayout lr
    }
  }
}