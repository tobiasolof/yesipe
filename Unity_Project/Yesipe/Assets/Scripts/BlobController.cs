using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;

[ExecuteAlways]
public class BlobController : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler, IPointerClickHandler
{
    public string shaderName = "Shader Graphs/Blob Shader 2D";

    public bool panWithForce;

    bool dragged;

    [HideInInspector]
    public Animator animator;

    [SerializeField]
    Button deselectSuggestion = default;

    public Color color;
    public float size = 1f, blobNoise = 2f;
    [Range(0f, 0.8f)]
    public float blobAmplitude = 0.3f;
    int maxColliders = 7;
    public float moveTowardsMultiplier = 10f;

    List<BlobController> colliders = new List<BlobController>();
    [HideInInspector]
    public Rigidbody2D rigidBody2D;
    SpriteRenderer sprite;
    RawImage rawImage;
    RectTransform rectTransform;

    Material tempMaterial;

    TMP_Text title;

    BlobAreaController blobArea;
    AppStateManager appStateManager;

    private bool selected;
    public bool Selected
    {
        get => appStateManager.selectedBlobs.Contains(this);
        set
        {
            if (value)
            {
                appStateManager.SelectBlob(this);
            }
            else
            {
                appStateManager.DeselectBlob(this);
            }
        }
    }

    private void Awake()
    {
        appStateManager = FindObjectOfType<AppStateManager>();

        animator = GetComponent<Animator>();
        rectTransform = GetComponent<RectTransform>();
        rigidBody2D = GetComponent<Rigidbody2D>();
        sprite = GetComponent<SpriteRenderer>();
        rawImage = GetComponent<RawImage>();
        blobArea = GetComponentInParent<BlobAreaController>();
        title = GetComponentInChildren<TMP_Text>();

        deselectSuggestion.onClick.AddListener(() => { appStateManager.DeselectBlob(this); });
    }

    private void Start()
    {
        CreateAndAssignMaterial();
        UpdateBlobProperties();
    }


    void Update()
    {
        if (!tempMaterial)
            CreateAndAssignMaterial();

        tempMaterial.SetVector("_SelfPos", transform.position);

        colliders = new List<BlobController>();
        foreach (var item in Physics2D.OverlapCircleAll(transform.position, 3f))
        {
            if (item.gameObject != gameObject && item.gameObject.layer == gameObject.layer)
            {
                colliders.Add(item.GetComponent<BlobController>());
            }
        }

        for (int i = 0; i < colliders.Count; i++)
        {
            Vector4 input = colliders[i].transform.position;
            input.w = colliders[i].size * Mathf.Pow(colliders[i].transform.localScale.x, 2);
            tempMaterial.SetVector($"Collider{i + 1}", input);
        }

        for (int i = colliders.Count; i <= maxColliders; i++)
        {
            tempMaterial.SetVector($"Collider{i + 1}", new Vector4());
        }
    }

    public void SetTitle(string title)
    {
        this.title.SetText(title);
    }

    void CreateAndAssignMaterial()
    {
        tempMaterial = new Material(Shader.Find(shaderName));
        if (sprite)
            sprite.material = tempMaterial;
        if (rawImage)
            rawImage.material = tempMaterial;
    }

    [ContextMenu("Update Blob Values")]
    void UpdateBlobProperties()
    {
        tempMaterial.SetFloat("_OwnSize", size);
        tempMaterial.SetFloat("_BlobAmplitude", blobAmplitude);
        tempMaterial.SetFloat("_BlobNoise", blobNoise);
        tempMaterial.SetVector("_Color", color);
    }

    public void SetTargetPosition(Vector2 targetPos, bool killAfter, float maxTime = 0f)
    {
        try
        {
            StopCoroutine(MoveTowards);
        }
        catch
        {

        }
        MoveTowards = StartCoroutine(MoveTowardsPoint(targetPos, killAfter, maxTime));
    }

    Coroutine MoveTowards;

    IEnumerator MoveTowardsPoint(Vector2 targetPos, bool killAfter, float maxTime = 0f)
    {
        float timer = 0f;
        maxTime = maxTime == 0f ? Mathf.Infinity : maxTime;

        while ((targetPos - (Vector2)transform.position).magnitude > 1f && timer < maxTime)
        {
            timer += Time.deltaTime;

            Vector2 force = targetPos - (Vector2)transform.position;
            force *= moveTowardsMultiplier;
            rigidBody2D.AddForce(force);
            yield return null;
        }
        if (killAfter)
        {
            Destroy(gameObject);
        }
    }

    public void OnDrag(PointerEventData eventData)
    {
        if (Selected)
        {
            return;
        }
        if (panWithForce)
        {
            rigidBody2D.AddForce(eventData.delta / Screen.width * 15000f);
            blobArea.PanBlobs(eventData.delta / 4f);
        }
        else
        {
            //Vector2 newPos = (eventData.position - new Vector2(Screen.currentResolution.width / 2, Screen.currentResolution.height / 2)) / blobArea.canvasScaleFactor;
            Vector2 newPos = eventData.pointerCurrentRaycast.worldPosition;
            //newPos.x -= Screen.currentResolution.width * blobArea.canvasScaleFactor / 2;
            //newPos.y -= Screen.currentResolution.height * blobArea.canvasScaleFactor / 2;
            rigidBody2D.MovePosition(newPos);
            //rigidBody2D.MovePosition(eventData.pointerCurrentRaycast.worldPosition);
            blobArea.PanBlobs(eventData.delta / 2f);
        }
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        if (Selected)
        {
            return;
        }
        StopCoroutine(MoveTowards);
        dragged = true;
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        if (dragged || Selected)
        {
            return;
        }
        StopCoroutine(MoveTowards);
        appStateManager.SelectBlob(this);
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        dragged = false;
    }

}
