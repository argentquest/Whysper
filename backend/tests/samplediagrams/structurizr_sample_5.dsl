workspace {
  model {
    dev = person "Developer"
    repo = softwareSystem "Repository" {
      git = container "Git Server"
      dev -> git "Pushes code"
    }
  }
  views {
    systemContext repo {
      include *
      autolayout lr
    }
  }
}