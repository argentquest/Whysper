workspace {
  model {
    researcher = person "Researcher"
    dataSystem = softwareSystem "Data Analysis System" {
      container ui "UI"
      container processor "Data Processor"
      container storage "Data Storage"
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