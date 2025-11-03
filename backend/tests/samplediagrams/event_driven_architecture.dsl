
workspace {

    model {
        softwareSystem = softwareSystem "Event Processing System" {
            producer = container "Event Producer"
            broker = container "Message Broker"
            consumer = container "Event Consumer"

            producer -> broker "Publishes events"
            broker -> consumer "Delivers events"
        }
    }

    views {
        container softwareSystem {
            include *
            autolayout lr
        }
        theme default
    }
}
