using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;

[ExecuteAlways]
public class BlobController : MonoBehaviour, IDragHandler
{
    public bool panWithForce;

    public Color color;
    public float size = 1f, blobNoise = 2f;
    [Range(0f, 0.8f)]
    public float blobAmplitude = 0.3f;
    int maxColliders = 7;

    List<BlobController> colliders = new List<BlobController>();
    [HideInInspector]
    public Rigidbody2D rigidBody2D;
    SpriteRenderer sprite;
    RawImage rawImage;
    
    Material tempMaterial;
    
    TMP_Text title;

    BlobAreaController blobArea;

    private void Awake()
    {
        rigidBody2D = GetComponent<Rigidbody2D>();
        sprite = GetComponent<SpriteRenderer>();
        rawImage = GetComponent<RawImage>();
        blobArea = GetComponentInParent<BlobAreaController>();
        title = GetComponentInChildren<TMP_Text>();
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
            if (item.gameObject != gameObject)
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
        tempMaterial = new Material(Shader.Find("Shader Graphs/Blob Shader 2D"));
        tempMaterial.SetVector("_Color", color);
        if (sprite)
            sprite.material = tempMaterial;
        if (rawImage)
            rawImage.material = tempMaterial;
    }

    void UpdateBlobProperties()
    {
        tempMaterial.SetFloat("_OwnSize", size);
        tempMaterial.SetFloat("_BlobAmplitude", blobAmplitude);
        tempMaterial.SetFloat("_BlobNoise", blobNoise);
    }

    public void SetTargetPosition(Vector2 targetPos, bool killAfter, float maxTime = 0f)
    {
        StartCoroutine(MoveTowardsPoint(targetPos, killAfter, maxTime));
    }

    IEnumerator MoveTowardsPoint(Vector2 targetPos, bool killAfter, float maxTime = 0f)
    {
        float timer = 0f;
        maxTime = maxTime == 0f ? Mathf.Infinity : maxTime;

        while ((targetPos - (Vector2)transform.position).magnitude > 1f && timer < maxTime)
        {
            timer += Time.deltaTime;

            Vector2 force = targetPos - (Vector2)transform.position;
            force *= 10f;
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
        if (panWithForce)
        {
            rigidBody2D.AddForce(eventData.delta / Screen.width * 15000f);
            blobArea.PanBlobs(eventData.delta / 4f);
        }
        else
        {
            rigidBody2D.MovePosition(eventData.pointerCurrentRaycast.worldPosition);
            blobArea.PanBlobs(eventData.delta / 2f);
        }
    }
}
