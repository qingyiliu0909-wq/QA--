#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EM Asset Naming Rules Check Script. Usage: python check_naming_rules.py [path]"""

import json
import sys
import os


KNOWN_CLASSES = {
    "StaticMesh", "SkeletalMesh", "Texture2D", "Texture",
    "Texture2DArray", "TextureCube", "TextureRenderTarget2D",
    "TextureRenderTargetCube", "VolumeTexture",
    "Material", "MaterialInstance", "MaterialInstanceConstant",
    "LevelSequence", "AnimSequence", "AnimMontage",
    "Blueprint", "SoundWave", "ParticleSystem",
}


def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] file not found: {}".format(path))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print("[ERROR] JSON syntax error: {}".format(e))
        sys.exit(1)
    return data


def get_class_names(t):
    """Normalize 'class' field to list. Accepts string or array."""
    cls = t.get("class", "")
    if isinstance(cls, list):
        return cls
    return [cls] if cls else []


def check_top_level_fields(data):
    errors = []
    for field in ["assetTypes", "defaultValidation"]:
        if field not in data:
            errors.append("missing required field '{}'".format(field))
    if "ignorePaths" in data and not isinstance(data["ignorePaths"], list):
        errors.append("'ignorePaths' must be an array")
    if "ignoreClasses" in data and not isinstance(data["ignoreClasses"], list):
        errors.append("'ignoreClasses' must be an array")
    if "enabled" in data and not isinstance(data["enabled"], bool):
        errors.append("'enabled' must be a boolean")
    return errors


def check_asset_types(asset_types, scope_name="global"):
    errors = []
    warns = []

    for i, t in enumerate(asset_types):
        class_names = get_class_names(t)
        pfx = t.get("prefix", "")
        sfx = t.get("suffix", "")

        for cls in class_names:
            if cls not in KNOWN_CLASSES:
                warns.append(
                    "{} assetTypes[{}]: unknown class '{}', "
                    "expected one of: {}".format(
                        scope_name, i, cls, ", ".join(sorted(KNOWN_CLASSES))))
        if not class_names:
            warns.append(
                "{} assetTypes[{}]: 'class' field is empty".format(scope_name, i))
        if pfx == "" and sfx == "":
            warns.append(
                "{} assetTypes[{}]({}): prefix and suffix are both empty, "
                "this type cannot be identified by name".format(
                    scope_name, i, ", ".join(class_names)))

        for j in range(i + 1, len(asset_types)):
            t2 = asset_types[j]
            names2 = get_class_names(t2)
            for cn in class_names:
                if cn in names2:
                    errors.append(
                        "{} assetTypes: duplicate class '{}' "
                        "(entry {} and {})".format(scope_name, cn, i, j))
            if pfx == t2.get("prefix", "") and sfx == t2.get("suffix", ""):
                errors.append(
                    "{} assetTypes: duplicate prefix='{}' suffix='{}' "
                    "(entry {} and {})".format(scope_name, pfx, sfx, i, j))

    return errors, warns


def check_validation_entries(asset_types, validation, scope_name="global"):
    errors = []
    warns = []

    # Build class→assetType map (each class name maps to its definition)
    type_map = {}
    for t in asset_types:
        for cls in get_class_names(t):
            if cls not in type_map:
                type_map[cls] = t

    seen_classes = set()
    for vi, entry in enumerate(validation):
        class_names = get_class_names(entry)
        constraints = entry.get("constraints", [])

        for cls in class_names:
            if cls in seen_classes:
                errors.append(
                    "{} validation[{}]: duplicate class '{}'".format(
                        scope_name, vi, cls))
            seen_classes.add(cls)

        if not class_names:
            warns.append("{} validation[{}]: 'class' field is empty".format(scope_name, vi))
            continue

        # Use first class name for display; check against all class names
        cls_display = class_names[0]

        # Explicitly disabled entry — skip constraint consistency checks.
        # Used in pathRules to suppress a class without re-declaring constraints.
        if entry.get("enabled") is False:
            continue

        # Find matching assetType (any class name match)
        asset_type = None
        for cls in class_names:
            if cls in type_map:
                asset_type = type_map[cls]
                break

        if not asset_type:
            warns.append(
                "{} validation[{}]: class='{}' is not defined in assetTypes, "
                "this validation will never be applied".format(
                    scope_name, vi, cls_display))
            continue

        pfx_expected = asset_type.get("prefix", "")
        sfx_expected = asset_type.get("suffix", "")

        prefix_constraints = [c for c in constraints
                              if c.get("type") == "Prefix"]
        allow_prefix_constraints = [c for c in constraints
                                    if c.get("type") == "AllowPrefix"]
        suffix_constraints = [c for c in constraints
                              if c.get("type") == "Suffix"]
        allow_suffix_constraints = [c for c in constraints
                                    if c.get("type") == "AllowSuffix"]

        if pfx_expected:
            if len(prefix_constraints) != 1:
                errors.append(
                    "{} {}: assetType requires prefix='{}', "
                    "but validation has {} Prefix constraints "
                    "(expected exactly 1)".format(
                        scope_name, cls_display, pfx_expected,
                        len(prefix_constraints)))
            else:
                # Value must match either Prefix or AllowPrefix
                all_pfx = prefix_constraints + allow_prefix_constraints
                matched = [c for c in all_pfx if c.get("value") == pfx_expected]
                if not matched:
                    errors.append(
                        "{} {}: assetType prefix='{}' does not match "
                        "any Prefix or AllowPrefix constraint".format(
                            scope_name, cls_display, pfx_expected))
        elif len(prefix_constraints) > 0:
            warns.append(
                "{} {}: assetType has no prefix, "
                "but validation has {} Prefix constraints".format(
                    scope_name, cls_display, len(prefix_constraints)))

        if sfx_expected:
            # Exactly 1 Suffix constraint required, value match via Suffix or AllowSuffix.
            suffix_matched = [c for c in suffix_constraints if c.get("value") == sfx_expected]
            allow_matched  = [c for c in allow_suffix_constraints if c.get("value") == sfx_expected]
            if len(suffix_constraints) != 1 or not (suffix_matched or allow_matched):
                errors.append(
                    "{} {}: assetType requires suffix='{}', "
                    "but validation has {} Suffix constraints (expected exactly 1)".format(
                        scope_name, cls_display, sfx_expected, len(suffix_constraints)))
        elif len(suffix_constraints) > 0:
            warns.append(
                "{} {}: assetType has no suffix, "
                "but validation has {} Suffix constraints".format(
                    scope_name, cls_display, len(suffix_constraints)))

        for ci, c in enumerate(constraints):
            if c.get("type") not in ("Prefix", "Suffix", "AllowPrefix", "AllowSuffix"):
                errors.append(
                    "{} {} constraint[{}]: "
                    "type must be 'Prefix', 'Suffix', 'AllowPrefix' or 'AllowSuffix'".format(
                        scope_name, cls_display, ci))
            if c.get("scope") not in ("Both", "Editor", "CI", None):
                errors.append(
                    "{} {} constraint[{}]: "
                    "scope must be 'Both', 'Editor' or 'CI'".format(
                        scope_name, cls_display, ci))
            if "value" not in c or not c["value"]:
                errors.append(
                    "{} {} constraint[{}]: value is empty".format(
                        scope_name, cls_display, ci))
            # replaceFrom — valid only on Prefix, accepts string or array
            rf = c.get("replaceFrom")
            if rf is not None:
                if c.get("type") != "Prefix":
                    errors.append(
                        "{} {} constraint[{}]: replaceFrom is only valid on Prefix type".format(
                            scope_name, cls_display, ci))
                elif not isinstance(rf, (str, list)):
                    errors.append(
                        "{} {} constraint[{}]: replaceFrom must be a string or array".format(
                            scope_name, cls_display, ci))

    for cls in type_map:
        if cls not in seen_classes:
            warns.append(
                "{}: class='{}' is defined in assetTypes "
                "but has no validation entry".format(scope_name, cls))

    return errors, warns


def check_path_rules(global_types, global_validation, path_rules):
    errors = []
    warns = []

    if not path_rules:
        return errors, warns

    for ri, rule in enumerate(path_rules):
        path = rule.get("path", "")
        if not path:
            errors.append("pathRules[{}]: missing 'path' field".format(ri))
            continue

        scope = "pathRules[{}] (path='{}')".format(ri, path)

        local_types = rule.get("assetTypes", [])
        types_to_use = local_types if local_types else global_types
        validation = rule.get("validation", [])

        e, w = check_asset_types(local_types, scope)
        errors += e
        warns += w

        # Collect all class names in scope (local types if present, else global)
        scoped_classes = set()
        for t in types_to_use:
            for cls in get_class_names(t):
                scoped_classes.add(cls)

        # Build merged validation: pathRule overrides covered classes,
        # global default fills gaps for classes in scope.
        merged_val = [gve for gve in global_validation
                      if scoped_classes.intersection(get_class_names(gve))]
        for pve in validation:
            pve_classes = set(get_class_names(pve))
            merged_val = [gve for gve in merged_val
                          if not pve_classes.intersection(get_class_names(gve))]
            merged_val.append(pve)

        e, w = check_validation_entries(types_to_use, merged_val, scope)
        errors += e
        warns += w

        if not validation:
            warns.append(
                "{}: has no validation entries, "
                "assets under this path will NOT be checked".format(scope))

    return errors, warns


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(__file__), "DefaultAssetNamingRules.json")

    print("EM Asset Naming Rules Check")
    print("Config: {}".format(config_path))
    print("-" * 50)

    data = load_config(config_path)

    all_errors = []
    all_warns = []

    all_errors += check_top_level_fields(data)

    asset_types = data.get("assetTypes", [])
    e, w = check_asset_types(asset_types, "global")
    all_errors += e
    all_warns += w

    default_val = data.get("defaultValidation", [])
    e, w = check_validation_entries(asset_types, default_val, "global")
    all_errors += e
    all_warns += w

    path_rules = data.get("pathRules", [])
    e, w = check_path_rules(asset_types, default_val, path_rules)
    all_errors += e
    all_warns += w

    print()

    if all_warns:
        print("[WARN] {} warning(s):".format(len(all_warns)))
        for w in all_warns:
            print("  - {}".format(w))

    if all_errors:
        print("\n[ERROR] {} error(s):".format(len(all_errors)))
        for e in all_errors:
            print("  - {}".format(e))

    if not all_errors and not all_warns:
        print("[OK] All naming rules are valid.")
        print()
        print("Before committing, please verify:")
        print("  1. ignorePaths covers paths you want to exclude")
        print("  2. defaultValidation covers all asset types to be checked")
        print("  3. pathRules demo entries are enabled or removed")
        print("  4. All constraint scopes are correct (Both/Editor/CI)")
        sys.exit(0)
    elif all_errors:
        print("\n[FAIL] {} error(s), {} warning(s). Fix errors above.".format(
            len(all_errors), len(all_warns)))
        sys.exit(1)
    else:
        print("\n[WARN] {} warning(s) only. Config is usable but review above.".format(
            len(all_warns)))
        sys.exit(0)


if __name__ == "__main__":
    main()
