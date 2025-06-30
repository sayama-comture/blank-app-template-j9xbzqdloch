# คุณสมบัติการดูแลระบบ

## ข้อกำหนดเบื้องต้น

ผู้ใช้งานระดับผู้ดูแลระบบจะต้องเป็นสมาชิกของกลุ่มที่เรียกว่า `Admin` ซึ่งสามารถตั้งค่าได้ผ่านคอนโซลการจัดการ > Amazon Cognito User pools หรือ aws cli โปรดทราบว่าสามารถอ้างอิง ID ของผู้ใช้งานพูลได้โดยเข้าถึง CloudFormation > BedrockChatStack > Outputs > `AuthUserPoolIdxxxx`

![](./imgs/group_membership_admin.png)

## ทำเครื่องหมายบอทสาธารณะเป็นจำเป็น

ตอนนี้ผู้ดูแลระบบสามารถทำเครื่องหมายบอทสาธารณะเป็น "จำเป็น" ได้ บอทที่ทำเครื่องหมายว่าจำเป็นจะถูกแสดงในส่วน "จำเป็น" ของร้านค้าบอท ทำให้ผู้ใช้สามารถเข้าถึงได้อย่างง่ายดาย ซึ่งช่วยให้ผู้ดูแลระบบสามารถปักหมุดบอทที่สำคัญที่ต้องการให้ผู้ใช้ทุกคนใช้งาน

### ตัวอย่าง

- บอทผู้ช่วยฝ่ายทรัพยากรบุคคล: ช่วยเหลือพนักงานเกี่ยวกับคำถามและงานที่เกี่ยวข้องกับทรัพยากรบุคคล
- บอทสนับสนุนไอที: ให้ความช่วยเหลือปัญหาทางเทคนิคภายในและการจัดการบัญชี
- บอทคู่มือนโยบายภายใน: ตอบคำถามที่พบบ่อยเกี่ยวกับกฎการลา นโยบายความปลอดภัย และระเบียบภายในอื่นๆ
- บอทปฐมนิเทศพนักงานใหม่: แนะนำพนักงานใหม่ผ่านขั้นตอนและการใช้งานระบบในวันแรก
- บอทข้อมูลสวัสดิการ: อธิบายโปรแกรมสวัสดิการของบริษัทและบริการสวัสดิการ

![](./imgs/admin_bot_menue.png)
![](./imgs/bot_store.png)

## วงจรป้อนกลับ

เอาต์พุตจาก LLM อาจไม่ตรงตามความคาดหวังของผู้ใช้เสมอไป บางครั้งอาจไม่สามารถตอบสนองความต้องการของผู้ใช้ได้ เพื่อ "บูรณาการ" LLMs เข้ากับการดำเนินงานทางธุรกิจและชีวิตประจำวันอย่างมีประสิทธิภาพ การใช้วงจรป้อนกลับถือเป็นสิ่งสำคัญ Bedrock Chat มีคุณสมบัติการให้ข้อเสนอแนะที่ออกแบบมาเพื่อช่วยให้ผู้ใช้สามารถวิเคราะห์สาเหตุของความไม่พอใจได้ ขึ้นอยู่กับผลการวิเคราะห์ ผู้ใช้สามารถปรับแต่งพรอมต์ แหล่งข้อมูล RAG และพารามิเตอร์ต่าง ๆ ได้ตามความเหมาะสม

![](./imgs/feedback_loop.png)

![](./imgs/feedback-using-claude-chat.png)

นักวิเคราะห์ข้อมูลสามารถเข้าถึงบันทึกการสนทนาโดยใช้ [Amazon Athena](https://aws.amazon.com/jp/athena/) หากต้องการวิเคราะห์ข้อมูลด้วย [Jupyter Notebook](https://jupyter.org/) สามารถใช้[ตัวอย่างสมุดบันทึกนี้](../examples/notebooks/feedback_analysis_example.ipynb)เป็นแนวอ้างอิงได้

## แดชบอร์ด

ปัจจุบันให้ภาพรวมพื้นฐานของการใช้งานแชทบอทและผู้ใช้ โดยมุ่งเน้นการรวบรวมข้อมูลสำหรับแต่ละบอทและผู้ใช้ในช่วงเวลาที่กำหนด และจัดเรียงผลลัพธ์ตามค่าใช้จ่ายในการใช้งาน

![](./imgs/admin_bot_analytics.png)

## หมายเหตุ

- ตามที่ระบุไว้ใน [สถาปัตยกรรม](../README.md#architecture) คุณสมบัติของผู้ดูแลระบบจะอ้างอิงถึงบัคเก็ต S3 ที่ส่งออกมาจาก DynamoDB โปรดทราบว่าเนื่องจากการส่งออกจะดำเนินการทุกๆ หนึ่งชั่วโมง การสนทนาล่าสุดอาจไม่ปรากฏทันที

- ในการใช้งานบอทสาธารณะ บอทที่ไม่ได้ใช้งานเลยในช่วงเวลาที่ระบุจะไม่ถูกแสดง

- ในการใช้งานของผู้ใช้ ผู้ใช้ที่ไม่ได้ใช้ระบบเลยในช่วงเวลาที่ระบุจะไม่ถูกแสดง

> [!สำคัญ]
> หากคุณใช้งานหลายสภาพแวดล้อม (dev, prod เป็นต้น) ชื่อฐานข้อมูล Athena จะรวมคำนำหน้าสภาพแวดล้อม แทนที่จะเป็น `bedrockchatstack_usage_analysis` ชื่อฐานข้อมูลจะเป็น:
>
> - สำหรับสภาพแวดล้อมเริ่มต้น: `bedrockchatstack_usage_analysis`
> - สำหรับสภาพแวดล้อมที่มีชื่อ: `<คำนำหน้าสภาพแวดล้อม>_bedrockchatstack_usage_analysis` (เช่น `dev_bedrockchatstack_usage_analysis`)
>
> นอกจากนี้ ชื่อตารางจะรวมคำนำหน้าสภาพแวดล้อมด้วย:
>
> - สำหรับสภาพแวดล้อมเริ่มต้น: `ddb_export`
> - สำหรับสภาพแวดล้อมที่มีชื่อ: `<คำนำหน้าสภาพแวดล้อม>_ddb_export` (เช่น `dev_ddb_export`)
>
> ตรวจสอบให้แน่ใจว่าคุณปรับแก้การสอบถามของคุณให้เหมาะสมเมื่อทำงานกับหลายสภาพแวดล้อม

## ดาวน์โหลดข้อมูลการสนทนา

คุณสามารถค้นหาบันทึกการสนทนาโดยใช้ Athena ด้วย SQL เพื่อดาวน์โหลดบันทึก ให้เปิด Athena Query Editor จากคอนโซลการจัดการและรันคำสั่ง SQL ต่อไปนี้เป็นตัวอย่างคิวรีที่มีประโยชน์สำหรับวิเคราะห์กรณีการใช้งาน ข้อเสนอแนะสามารถอ้างอิงได้จากแอตทริบิวต์ `MessageMap`

### คิวรีตาม Bot ID

แก้ไข `bot-id` และ `datehour` `bot-id` สามารถอ้างอิงได้จากหน้าจัดการ Bot ซึ่งสามารถเข้าถึงได้จาก Bot Publish APIs ที่แสดงอยู่ที่แถบด้านซ้าย สังเกตส่วนท้ายของ URL เช่น `https://xxxx.cloudfront.net/admin/bot/<bot-id>`

```sql
SELECT
    d.newimage.PK.S AS UserId,
    d.newimage.SK.S AS ConversationId,
    d.newimage.MessageMap.S AS MessageMap,
    d.newimage.TotalPrice.N AS TotalPrice,
    d.newimage.CreateTime.N AS CreateTime,
    d.newimage.LastMessageId.S AS LastMessageId,
    d.newimage.BotId.S AS BotId,
    d.datehour AS DateHour
FROM
    bedrockchatstack_usage_analysis.ddb_export d
WHERE
    d.newimage.BotId.S = '<bot-id>'
    AND d.datehour BETWEEN '<yyyy/mm/dd/hh>' AND '<yyyy/mm/dd/hh>'
    AND d.Keys.SK.S LIKE CONCAT(d.Keys.PK.S, '#CONV#%')
ORDER BY
    d.datehour DESC;
```

> [!Note]
> หากใช้สภาพแวดล้อมที่มีชื่อ (เช่น "dev") ให้แทนที่ `bedrockchatstack_usage_analysis.ddb_export` ด้วย `dev_bedrockchatstack_usage_analysis.dev_ddb_export` ในคิวรีด้านบน

### คิวรีตาม User ID

แก้ไข `user-id` และ `datehour` `user-id` สามารถอ้างอิงได้จากหน้าจัดการ Bot

> [!Note]
> การวิเคราะห์การใช้งานของผู้ใช้กำลังจะมีเร็วๆ นี้

```sql
SELECT
    d.newimage.PK.S AS UserId,
    d.newimage.SK.S AS ConversationId,
    d.newimage.MessageMap.S AS MessageMap,
    d.newimage.TotalPrice.N AS TotalPrice,
    d.newimage.CreateTime.N AS CreateTime,
    d.newimage.LastMessageId.S AS LastMessageId,
    d.newimage.BotId.S AS BotId,
    d.datehour AS DateHour
FROM
    bedrockchatstack_usage_analysis.ddb_export d
WHERE
    d.newimage.PK.S = '<user-id>'
    AND d.datehour BETWEEN '<yyyy/mm/dd/hh>' AND '<yyyy/mm/dd/hh>'
    AND d.Keys.SK.S LIKE CONCAT(d.Keys.PK.S, '#CONV#%')
ORDER BY
    d.datehour DESC;
```

> [!Note]
> หากใช้สภาพแวดล้อมที่มีชื่อ (เช่น "dev") ให้แทนที่ `bedrockchatstack_usage_analysis.ddb_export` ด้วย `dev_bedrockchatstack_usage_analysis.dev_ddb_export` ในคิวรีด้านบน