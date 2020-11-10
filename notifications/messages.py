guests_notifications_texts = dict(
    subject="Nouvelle invitation sur PlanniTeam",
    user_message="Bonjour {user_name}. {creator_name} vous a invité au "
                 "planning {planning_name}.\nPour y participer, connectez "
                 "vous avec votre compte et rejoignez {planning_url}",
    new_user_message="Bonjour. {creator_name} vous a invité au planning"
                     " {planning_name}.\nPour y participer, créez un compte"
                     " sur {domain} avec cette adresse email et"
                     " rejoignez {planning_url} !",
)

events_changes_texts = dict(
    subject="Modification du planning {planning_name}",
    base_message="Bonjour {user_name} !\nDes changements ont eu lieu"
                 " sur le planning {planning_name}. Vous pouvez consulter"
                 " le planning sur {planning_url}.",
    added="ajoutés",
    modified="modifiés",
    deleted="supprimés",
    event_row="\nLes événements suivants ont été {action}: {events}.",
)
