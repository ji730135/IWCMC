graph [
  node [
    id 0
    label "0"
    type "T"
  ]
  node [
    id 1
    label "1"
    type "T"
  ]
  node [
    id 2
    label "2"
    type "T"
  ]
  node [
    id 3
    label "3"
    type "T"
  ]
  node [
    id 4
    label "4"
    type "M"
    peers 1
  ]
  node [
    id 5
    label "5"
    type "M"
    peers 1
  ]
  node [
    id 6
    label "6"
    type "C"
    peers 0
  ]
  node [
    id 7
    label "7"
    type "C"
    peers 0
  ]
  node [
    id 8
    label "8"
    type "C"
    peers 0
  ]
  node [
    id 9
    label "9"
    type "C"
    peers 0
  ]
  edge [
    source 0
    target 1
    type "peer"
    customer "none"
  ]
  edge [
    source 0
    target 2
    type "peer"
    customer "none"
  ]
  edge [
    source 0
    target 3
    type "peer"
    customer "none"
  ]
  edge [
    source 1
    target 2
    type "peer"
    customer "none"
  ]
  edge [
    source 1
    target 3
    type "peer"
    customer "none"
  ]
  edge [
    source 1
    target 4
    type "transit"
    customer "4"
  ]
  edge [
    source 1
    target 6
    type "transit"
    customer "6"
  ]
  edge [
    source 1
    target 9
    type "transit"
    customer "9"
  ]
  edge [
    source 2
    target 3
    type "peer"
    customer "none"
  ]
  edge [
    source 2
    target 4
    type "transit"
    customer "4"
  ]
  edge [
    source 2
    target 5
    type "transit"
    customer "5"
  ]
  edge [
    source 3
    target 4
    type "transit"
    customer "4"
  ]
  edge [
    source 3
    target 8
    type "transit"
    customer "8"
  ]
  edge [
    source 4
    target 5
    type "peer"
    customer "none"
  ]
  edge [
    source 5
    target 7
    type "transit"
    customer "7"
  ]
]
