using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class AppStateManager : MonoBehaviour
{
    public enum AppState
    {
        AddBubbles, SelectRecipe, ReadRecipe
    };

    private AppState currentAppState;
    public AppState CurrentAppState
    {
        get => currentAppState;
        set
        {
            switch (value)
            {
                case AppState.AddBubbles:
                    addBubblesToggle.SetIsOnWithoutNotify(true);
                    UIAnimator.SetTrigger("AddBubbles");
                    for (int i = 0; i < selectedBlobs.Count; i++)
                    {
                        BlobController blob = selectedBlobs[i];
                        blob.transform.SetParent(selectedBlobsParent);
                        blob.SetTargetPosition(selectedBlobsParent.GetChild(i).transform.position, false);
                    }
                    foreach (var blob in yesipeBackendProvider.activeSuggestions)
                    {
                        blob.SetTargetPosition(new Vector2(), false, Random.Range(0.5f, 1f));
                    }
                    break;

                case AppState.SelectRecipe:
                    if (!selectedRecipe)
                    {
                        UIAnimator.SetTrigger("ErrorMessage");
                        CurrentAppState = AppState.AddBubbles;
                        return;
                    }
                    for (int i = 0; i < selectedBlobs.Count; i++)
                    {
                        BlobController blob = selectedBlobs[i];
                        blob.transform.SetParent(yourPicksParent);
                        blob.SetTargetPosition(yourPicksParent.GetChild(i).transform.position, false);
                    }
                    foreach (var blob in yesipeBackendProvider.activeSuggestions)
                    {
                        blob.SetTargetPosition(blob.transform.position.normalized * 20f, false, 2f);
                    }
                    SetSelectedRecipe(selectedRecipe, 0);
                    selectRecipeToggle.SetIsOnWithoutNotify(true);
                    UIAnimator.SetTrigger("SelectRecipe");
                    break;

                case AppState.ReadRecipe:
                    readRecipeToggle.SetIsOnWithoutNotify(true);
                    UIAnimator.SetTrigger("ReadRecipe");
                    break;

                default:
                    break;
            }
            currentAppState = value;
        }
    }

    YesipeBackendProvider yesipeBackendProvider;
    [SerializeField]
    Animator UIAnimator = default;
    [SerializeField]
    Transform selectedBlobsParent = default, freeBlobsParent = default, yourPicksParent = default, addedKeyIngredientsParent = default;

    [SerializeField]
    public Toggle addBubblesToggle = default, selectRecipeToggle = default, readRecipeToggle = default;
    [SerializeField]
    public Button inspireMe = default;

    public List<BlobController> selectedBlobs = new List<BlobController>();

    public RecipeAlternative selectedRecipe; //TODO: not public
    public List<RecipeAlternative> recipeAlternatives = new List<RecipeAlternative>(); //TODO: not public
    [SerializeField]
    RectTransform listOfAlternatives = default;
    Vector2 recipeAlternativesTargetScrollPos, refScrollPos;

    int freeBlobsLayer = 8, selectedBlobsLayer = 9;

    private void Awake()
    {
        yesipeBackendProvider = FindObjectOfType<YesipeBackendProvider>();       

        addBubblesToggle.onValueChanged.AddListener((isOn) => { if (isOn) CurrentAppState = AppState.AddBubbles; });
        selectRecipeToggle.onValueChanged.AddListener((isOn) => { if (isOn) CurrentAppState = AppState.SelectRecipe; });
        readRecipeToggle.onValueChanged.AddListener((isOn) => { if (isOn) CurrentAppState = AppState.ReadRecipe; });

        inspireMe.onClick.AddListener(() =>
        {
            CurrentAppState = AppState.SelectRecipe;
            //TODO: Get recipes
        });
    }

    private void Start()
    {
        //SetSelectedRecipe(recipeAlternatives[0], true);//todo: remove this
    }

    private void Update()
    {
        if (Vector2.Distance(listOfAlternatives.anchoredPosition, recipeAlternativesTargetScrollPos) > 0.1f)
        {
            listOfAlternatives.anchoredPosition = Vector2.SmoothDamp(listOfAlternatives.anchoredPosition, recipeAlternativesTargetScrollPos, ref refScrollPos, 0.2f);
        }
    }

    #region blobs

    public void UpdateBlobs()
    {
        //TODO: Control blobs from here
    }
    
    public bool SelectBlob(BlobController blob)
    {
        if (selectedBlobs.Contains(blob))
        {
            Debug.LogWarning("Blob already selected!");
            return false;
        }
        yesipeBackendProvider.activeSuggestions.Remove(blob);
        yesipeBackendProvider.activeSuggestions.TrimExcess();
        selectedBlobs.Add(blob);
        blob.transform.SetParent(selectedBlobsParent);
        blob.gameObject.layer = selectedBlobsLayer;
        blob.SetTargetPosition(selectedBlobsParent.GetChild(selectedBlobs.Count - 1).transform.position, false);
        blob.animator.SetBool("selected", true);

        return true;
    }

    public bool DeselectBlob(BlobController blob)
    {
        if (!selectedBlobs.Contains(blob))
        {
            Debug.LogWarning("Blob not among selected!");
            return false;
        }
        selectedBlobs.Remove(blob);
        selectedBlobs.TrimExcess();
        blob.transform.SetParent(freeBlobsParent);
        blob.gameObject.layer = freeBlobsLayer;
        blob.SetTargetPosition(new Vector2(0f, 0f), false, 0.5f);
        blob.animator.SetBool("selected", false);

        return true;
    }
    #endregion

    #region select recipe

    public void UpdateRecipeSuggestions()
    {

    }

    public void SetSelectedRecipe(int newRecipeInt)
    {
        for (int i = 0; i < recipeAlternatives.Count; i++)
        {
            recipeAlternatives[i].animator.SetBool("selected", i == newRecipeInt);
        }

        selectedRecipe = recipeAlternatives[newRecipeInt];
        //recipeAlternatives[newRecipeInt].animator.SetBool("selected", true);

        recipeAlternativesTargetScrollPos = new Vector2(0f, 144f * (newRecipeInt - 1));
    }

    public void SetSelectedRecipe(RecipeAlternative prevAlternative, int chooseRecipeRelativeToLast)
    {
        int newAlternative = -1;

        for (int i = 0; i < recipeAlternatives.Count; i++)
        {
            //recipeAlternatives[i].animator.SetBool("selected", false);

            if (recipeAlternatives[i] == prevAlternative)
            {
                newAlternative = i + chooseRecipeRelativeToLast;
                newAlternative = Mathf.Clamp(newAlternative, 0, recipeAlternatives.Count - 1);
            }
        }
        SetSelectedRecipe(newAlternative);
    }

    #endregion
}
