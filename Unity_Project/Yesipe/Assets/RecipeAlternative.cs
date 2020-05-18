using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class RecipeAlternative : MonoBehaviour
{
    [SerializeField]
    TMP_Text recipeTitle, time, ingredients;
    [SerializeField]
    Image recipeImage;
    [SerializeField]
    Button upArrow = default, downArrow = default;

    AppStateManager app;
    [HideInInspector]
    public Animator animator;

    private void Awake()
    {
        app = FindObjectOfType<AppStateManager>();
        animator = GetComponent<Animator>();

        upArrow.onClick.AddListener(() => { app.SetSelectedRecipe(this, -1); });
        downArrow.onClick.AddListener(() => { app.SetSelectedRecipe(this, 1); });
    }
}
