#!/bin/sh
# Switch between different opencode auth profiles under ~/.local/share/opencode/auth.json
# Profiles are saved as auth-<profile_name>.json in the same directory.
# The currently active profile name is tracked in current_profile.txt.
#
# Usage:
#   ./oc-profiles.sh                   # interactive menu
#   ./oc-profiles.sh switch <profile>  # switch directly
#   ./oc-profile.sh save <profile>     # save current auth to profile
#   ./oc-profile.sh list               # list available profiles
#   ./oc-profile.sh current            # show current profile

# --------------------------------------------------------------------------- #
# Utility helpers
# --------------------------------------------------------------------------- #

die() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

info() {
    printf '%s\n' "$1"
}

warn() {
    printf 'Warning: %s\n' "$1" >&2
}

# --------------------------------------------------------------------------- #
# Path / state setup
# --------------------------------------------------------------------------- #

get_paths() {
    BASE_DIR=${OPENCODE_PROFILE_BASE_DIR:-"$HOME/.local/share/opencode"}
    AUTH_FILE="$BASE_DIR/auth.json"
    CURRENT_PROFILE_FILE="$BASE_DIR/current_profile.txt"
    PROFILES=
    PROFILE_COUNT=0
    CURRENT_RECORDED_PROFILE=
    VALID_CURRENT_PROFILE=
    CURRENT_STATUS=
}

ensure_base_dir() {
    if [ ! -d "$BASE_DIR" ]; then
        mkdir -p "$BASE_DIR" || die "Failed to create base directory: $BASE_DIR"
    fi
}

# --------------------------------------------------------------------------- #
# Profile list loading
# --------------------------------------------------------------------------- #

load_profiles() {
    PROFILES=
    PROFILE_COUNT=0

    for path in "$BASE_DIR"/auth-*.json; do
        [ -f "$path" ] || continue
        name=$(basename "$path")
        name=${name#auth-}
        name=${name%.json}

        if [ -z "$PROFILES" ]; then
            PROFILES="$name"
        else
            PROFILES=$(printf '%s\n%s' "$PROFILES" "$name")
        fi
    done

    if [ -n "$PROFILES" ]; then
        PROFILES=$(printf '%s\n' "$PROFILES" | sort)
        # Count lines safely
        PROFILE_COUNT=$(printf '%s\n' "$PROFILES" | wc -l | tr -d ' ')
    fi
}

# --------------------------------------------------------------------------- #
# Current profile status
# --------------------------------------------------------------------------- #

get_current_status() {
    CURRENT_RECORDED_PROFILE=
    VALID_CURRENT_PROFILE=
    CURRENT_STATUS=

    if [ -f "$CURRENT_PROFILE_FILE" ]; then
        IFS= read -r CURRENT_RECORDED_PROFILE < "$CURRENT_PROFILE_FILE" || CURRENT_RECORDED_PROFILE=
        if [ -n "$CURRENT_RECORDED_PROFILE" ] && [ -f "$BASE_DIR/auth-$CURRENT_RECORDED_PROFILE.json" ]; then
            VALID_CURRENT_PROFILE="$CURRENT_RECORDED_PROFILE"
            CURRENT_STATUS="$CURRENT_RECORDED_PROFILE"
        elif [ -n "$CURRENT_RECORDED_PROFILE" ]; then
            CURRENT_STATUS="$CURRENT_RECORDED_PROFILE (profile file missing)"
        else
            CURRENT_STATUS="unset (empty tracking file)"
        fi
    elif [ -f "$AUTH_FILE" ]; then
        CURRENT_STATUS="unknown (auth.json exists but no profile was ever saved via this tool)"
    else
        CURRENT_STATUS="unset (no auth.json)"
    fi
}

# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #

validate_profile_name() {
    _name=$1
    case $_name in
        '')
            info 'Profile name cannot be empty.'
            return 1
            ;;
        *[!A-Za-z0-9_-]*)
            info 'Profile name may only contain letters, numbers, underscores, and hyphens.'
            return 1
            ;;
        *)
            return 0
            ;;
    esac
}

# --------------------------------------------------------------------------- #
# Core operations
# --------------------------------------------------------------------------- #

write_current_profile() {
    printf '%s\n' "$1" > "$CURRENT_PROFILE_FILE" \
        || die 'Failed to update current_profile.txt'
}

switch_to_profile() {
    _profile=$1
    _source="$BASE_DIR/auth-$_profile.json"

    [ -f "$_source" ] || die "Profile not found: '$_profile'. Run with 'list' to see available profiles."

    # Warn if opencode may be running (best-effort; pgrep may not exist everywhere)
    if command -v pgrep > /dev/null 2>&1 && pgrep -x opencode > /dev/null 2>&1; then
        warn "opencode appears to be running. Close it before switching profiles, then restart it."
    fi

    cp "$_source" "$AUTH_FILE" || die "Failed to copy profile to auth.json"
    write_current_profile "$_profile"
    info "Switched to profile '$_profile'."
}

save_current_to_profile() {
    _profile=$1
    _target="$BASE_DIR/auth-$_profile.json"

    [ -f "$AUTH_FILE" ] || die "No auth.json found at '$AUTH_FILE'. Nothing to save."

    cp "$AUTH_FILE" "$_target" || die "Failed to save profile '$_profile'"
    write_current_profile "$_profile"
    info "Saved current auth.json to profile '$_profile'."
}

# --------------------------------------------------------------------------- #
# CLI mode (non-interactive)
# --------------------------------------------------------------------------- #

cmd_list() {
    load_profiles
    get_current_status
    info "Current profile: $CURRENT_STATUS"
    info ""
    if [ "$PROFILE_COUNT" -eq 0 ]; then
        info "No saved profiles found in $BASE_DIR"
        info "Tip: run with 'save <name>' to save your current auth.json as a profile."
    else
        info "Available profiles:"
        printf '%s\n' "$PROFILES" | while IFS= read -r p; do
            if [ "$p" = "$VALID_CURRENT_PROFILE" ]; then
                printf '  * %s  (active)\n' "$p"
            else
                printf '    %s\n' "$p"
            fi
        done
    fi
}

cmd_current() {
    get_current_status
    info "$CURRENT_STATUS"
}

cmd_switch() {
    _target=$1
    [ -n "$_target" ] || die "Usage: $0 switch <profile_name>"
    validate_profile_name "$_target" || exit 1
    switch_to_profile "$_target"
}

cmd_save() {
    _name=$1
    [ -n "$_name" ] || die "Usage: $0 save <profile_name>"
    validate_profile_name "$_name" || exit 1

    _target="$BASE_DIR/auth-$_name.json"
    if [ -f "$_target" ]; then
        printf "Profile '%s' already exists. Overwrite? [y/N]: " "$_name"
        IFS= read -r _ans || _ans=
        case $_ans in
            y|yes) ;;
            *) info "Aborted."; exit 0 ;;
        esac
    fi
    save_current_to_profile "$_name"
}

# --------------------------------------------------------------------------- #
# Interactive menu
# --------------------------------------------------------------------------- #

print_header() {
    printf '\n=== OpenCode Profile Switcher ===\n'
    printf 'Base directory : %s\n' "$BASE_DIR"
    printf 'Current profile: %s\n\n' "$CURRENT_STATUS"
}

print_profile_list() {
    if [ "$PROFILE_COUNT" -eq 0 ]; then
        return 0
    fi
    _idx=1
    printf '%s\n' "$PROFILES" | while IFS= read -r _p; do
        if [ "$_p" = "$VALID_CURRENT_PROFILE" ]; then
            printf '%s) %s  (active)\n' "$_idx" "$_p"
        else
            printf '%s) %s\n' "$_idx" "$_p"
        fi
        _idx=$((_idx + 1))
    done
}

prompt_profile_selection() {
    if [ "$PROFILE_COUNT" -eq 0 ]; then
        info "No saved profiles found. Use option 2 to save the current auth.json first."
        return 1
    fi

    print_profile_list

    while :; do
        printf 'Select a profile [1-%s, q]: ' "$PROFILE_COUNT"
        IFS= read -r _sel || return 1
        case $_sel in
            q|quit) return 1 ;;
            ''|*[!0-9]*)
                info 'Please enter a number or q.'
                ;;
            *)
                if [ "$_sel" -lt 1 ] || [ "$_sel" -gt "$PROFILE_COUNT" ]; then
                    info "Please enter a number from 1 to $PROFILE_COUNT."
                else
                    _idx=1
                    _chosen=
                    printf '%s\n' "$PROFILES" | while IFS= read -r _p; do
                        if [ "$_idx" -eq "$_sel" ]; then
                            printf '%s' "$_p"
                        fi
                        _idx=$((_idx + 1))
                    done | { IFS= read -r _chosen && switch_to_profile "$_chosen"; }
                    return 0
                fi
                ;;
        esac
    done
}

prompt_save_profile_name() {
    [ -f "$AUTH_FILE" ] || { info "No auth.json found. Nothing to save."; return 1; }

    while :; do
        if [ -n "$VALID_CURRENT_PROFILE" ]; then
            printf 'Profile name [%s]: ' "$VALID_CURRENT_PROFILE"
        else
            printf 'Profile name: '
        fi

        IFS= read -r _name || return 1

        case $_name in
            q|quit) return 1 ;;
        esac

        if [ -z "$_name" ] && [ -n "$VALID_CURRENT_PROFILE" ]; then
            _name="$VALID_CURRENT_PROFILE"
        fi

        validate_profile_name "$_name" || continue

        _target="$BASE_DIR/auth-$_name.json"
        if [ -f "$_target" ]; then
            printf "Profile '%s' already exists. Overwrite? [y/N]: " "$_name"
            IFS= read -r _ans || return 1
            case $_ans in
                y|yes) ;;
                q|quit) return 1 ;;
                *) continue ;;
            esac
        fi

        save_current_to_profile "$_name"
        return 0
    done
}

interactive_menu() {
    while :; do
        load_profiles
        get_current_status
        print_header

        printf '1) Switch to a profile\n'
        printf '2) Save current auth.json to a profile\n'
        printf '3) List all profiles\n'
        printf 'q) Quit\n'
        printf '\nChoose an action [1-3, q]: '

        IFS= read -r _action || _action=q

        printf '\n'
        case $_action in
            1) prompt_profile_selection || : ;;
            2) prompt_save_profile_name || : ;;
            3) cmd_list ;;
            q|quit) info "Goodbye."; exit 0 ;;
            *) info "Invalid choice. Please enter 1, 2, 3, or q." ;;
        esac
    done
}

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

main() {
    get_paths
    ensure_base_dir

    case ${1:-} in
        switch)  cmd_switch  "${2:-}" ;;
        save)    cmd_save    "${2:-}" ;;
        list)    cmd_list ;;
        current) cmd_current ;;
        ''|-i)   interactive_menu ;;
        -h|--help)
            printf 'Usage: %s [switch|save|list|current] [profile_name]\n' "$0"
            printf '\n  (no args)        interactive menu\n'
            printf '  switch <name>    switch to a saved profile\n'
            printf '  save <name>      save current auth.json as a profile\n'
            printf '  list             list all profiles\n'
            printf '  current          print current profile name\n'
            exit 0
            ;;
        *)
            die "Unknown command: '$1'. Run with --help for usage."
            ;;
    esac
}

main "$@"
