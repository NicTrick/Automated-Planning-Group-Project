;Header and description

(define (domain sokodomain)
    (:requirements :typing )

    (:types tile agent interactable - object
            soko - agent
            box key zone door - interactable
    )

    ;todo: define predicates here
    (:predicates 
        (at ?a - agent ?t - tile)

        (boxat ?b - box ?t - tile)
        (keyat ?k - key ?t - tile)
        (zoneat ?z - zone ?t - tile)
        (doorat ?d - door ?t - tile)

        (path ?t1 - tile ?t2 - tile)

        (haskey ?a - agent ?k - key)
        (hasbox ?a - agent ?b - box)

        (opens ?k - key ?d - door)      ; needs to be defined between key and door in the problem file
        (matches ?b - box ?z - zone)    ; needs to be defined between box and zone in the problem file

        (doorlocked ?d - door)
    )

    ; todo: define actions here
    ;; Move to adjacent tile (no door)
    (:action move
        :parameters (?a - agent ?from - tile ?to - tile)
        :precondition (and
        (at ?a ?from)
        (path ?from ?to)
        (not (exists (?d - door)
            (and (doorat ?d ?to) (doorlocked ?d))
            ))
        )
        :effect (and
        (not (at ?a ?from))
        (at ?a ?to)
        )
  ) 

  ;; Move through a door
    (:action move-through-door
        :parameters (
            ?a - agent ?from - tile ?to - tile ?d - door ?k - key
        )
        :precondition (and
        (at ?a ?from)
        (path ?from ?to)
        (doorat ?d ?to)
        (doorlocked ?d)
        (haskey ?a ?k)
        (opens ?k ?d)
        )
        :effect (and
        (not (at ?a ?from))
        (at ?a ?to)
        (not (doorlocked ?d))
        )
    )

    ;; Pick up key
    (:action take-key
        :parameters (
            ?a - agent ?k - key ?t - tile
        )
        :precondition (and
        (at ?a ?t)
        (keyat ?k ?t)
        )
        :effect (and
        (haskey ?a ?k)
        (not (keyat ?k ?t))
        )
    )

    ;; Lift box
    (:action lift-box
        :parameters (
            ?a - agent ?b - box ?t - tile
        )
        :precondition (and
        (at ?a ?t)
        (boxat ?b ?t)
        (not (exists (?x - box) (hasbox ?a ?x)))
        )
        :effect (and
        (hasbox ?a ?b)
        (not (boxat ?b ?t))
        )
    )

    ;; Drop box at matching zone
    (:action drop-box
        :parameters (
            ?a - agent ?b - box ?z - zone ?t - tile
        )
        :precondition (and
        (at ?a ?t)
        (zoneat ?z ?t)
        (hasbox ?a ?b)
        (matches ?b ?z)
        )
        :effect (and
        (not (hasbox ?a ?b))
        (boxat ?b ?t)
        )
    )

)